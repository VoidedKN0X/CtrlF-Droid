"""Find out who signed an APK, two independent ways, and fail on anything odd.

* `signer_sha256s` reads the signer certificates straight out of the v2/v3/v3.1
  APK Signing Block. Pure Python (standard library only), so it doesn't trust
  androguard or any other APK parser. It does NOT check the signatures: on its
  own it would accept an APK that carries a copy of the owner's certificate
  next to a forged signature. It exists as a second opinion and to reject
  malformed or ambiguous APKs (duplicate blocks, a fake ZIP end record).
* `verified_signer_sha256s` runs Google's `apksigner verify`, which checks the
  signatures cryptographically (every signer, every scheme, v3 key-rotation
  lineage, and that v1/v2/v3 agree), and returns the certificates of the
  signers it verified. This is the check that actually proves who signed it.

add_apk.py requires both lists to contain only allowed certificates.

    python scripts/apk_signers.py <apk>...   # prints "<sha256>  <apk>" per signer
"""
import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

V2_ID = 0x7109871A
V3_ID = 0xF05368C0
V31_ID = 0x1B93AD61
MAGIC = b"APK Sig Block 42"
EOCD_SIG = b"PK\x05\x06"
EOCD_LEN = 22


class ApkError(Exception):
    pass


def _lp(buf, off):
    """Read a uint32 length-prefixed slice starting at off; return (slice, next offset)."""
    if off + 4 > len(buf):
        raise ApkError("truncated length prefix")
    (n,) = struct.unpack_from("<I", buf, off)
    off += 4
    if off + n > len(buf):
        raise ApkError("length prefix runs past the end of its block")
    return buf[off : off + n], off + n


def _seq(buf):
    off = 0
    while off < len(buf):
        item, off = _lp(buf, off)
        yield item


def _eocd(f, size):
    """Offset of the ZIP End of Central Directory record, found the way apksig does.

    Search backwards for a record whose comment length reaches exactly to the end
    of the file, so a fake record hidden inside the ZIP comment can't be picked.
    """
    tail_len = min(size, 0xFFFF + EOCD_LEN)
    f.seek(size - tail_len)
    tail = f.read(tail_len)
    for pos in range(len(tail) - EOCD_LEN, -1, -1):
        if tail[pos : pos + 4] != EOCD_SIG:
            continue
        (comment_len,) = struct.unpack_from("<H", tail, pos + 20)
        if pos + EOCD_LEN + comment_len == len(tail):
            return size - tail_len + pos, tail[pos : pos + EOCD_LEN]
    raise ApkError("not a ZIP file (no end of central directory)")


def _signing_block(f):
    f.seek(0, 2)
    size = f.tell()
    eocd_off, eocd = _eocd(f, size)
    if eocd[4:8] != b"\x00\x00\x00\x00":
        raise ApkError("multi-disk ZIP")
    (cd_size, cd_offset) = struct.unpack_from("<II", eocd, 12)
    if cd_offset == 0xFFFFFFFF or cd_size == 0xFFFFFFFF:
        raise ApkError("ZIP64 APKs are not supported")
    if cd_offset + cd_size != eocd_off:
        raise ApkError("central directory doesn't end at the end of central directory record")
    if cd_offset < 32:
        raise ApkError("bad central directory offset")
    f.seek(cd_offset - 24)
    footer = f.read(24)
    if footer[8:] != MAGIC:
        raise ApkError("no APK Signing Block (v1-only or unsigned APK)")
    (block_size,) = struct.unpack_from("<Q", footer, 0)
    start = cd_offset - block_size - 8
    if start < 0 or block_size < 24 or block_size > size:
        raise ApkError("bad APK Signing Block size")
    f.seek(start)
    block = f.read(block_size + 8)
    if len(block) != block_size + 8 or struct.unpack_from("<Q", block, 0)[0] != block_size:
        raise ApkError("APK Signing Block sizes don't match")
    pairs = {}
    off, end = 8, len(block) - 24
    while off < end:
        if off + 12 > end:
            raise ApkError("truncated ID-value pair")
        (n,) = struct.unpack_from("<Q", block, off)
        if n < 4 or off + 8 + n > end:
            raise ApkError("bad ID-value pair length")
        (pid,) = struct.unpack_from("<I", block, off + 8)
        if pid in pairs:
            # Different parsers pick the first or the last copy; refuse the ambiguity.
            raise ApkError(f"APK Signing Block has more than one block with ID {pid:#010x}")
        pairs[pid] = block[off + 12 : off + 8 + n]
        off += 8 + n
    return pairs


def _scheme_certs(value):
    """First certificate of every signer in a v2/v3 signature scheme block."""
    certs = []
    signers, rest = _lp(value, 0)
    if rest != len(value):
        raise ApkError("trailing data after the signers")
    for signer in _seq(signers):
        signed_data, _ = _lp(signer, 0)
        _digests, off = _lp(signed_data, 0)
        cert_seq, _ = _lp(signed_data, off)
        first = next(_seq(cert_seq), None)
        if not first:
            raise ApkError("signer without a certificate")
        certs.append(first)
    if not certs:
        raise ApkError("signature scheme block without signers")
    return certs


def signer_sha256s(path):
    """SHA-256 fingerprints (lowercase hex) of every v2/v3/v3.1 signer certificate.

    Only parses; does not verify any signature. Raises ApkError if the APK has
    no v2+ signature or its signing block is malformed or ambiguous.
    """
    with open(path, "rb") as f:
        pairs = _signing_block(f)
    found = set()
    for pid in (V2_ID, V3_ID, V31_ID):
        if pid in pairs:
            found.update(hashlib.sha256(c).hexdigest() for c in _scheme_certs(pairs[pid]))
    if not found:
        raise ApkError("no v2/v3 signature in the APK Signing Block")
    return sorted(found)


def find_apksigner():
    """Path to apksigner: $APKSIGNER, then PATH. Never falls back to anything weaker."""
    path = os.environ.get("APKSIGNER") or shutil.which("apksigner")
    if not path or not Path(path).is_file():
        raise ApkError("apksigner not found; refusing to publish without verifying signatures")
    return path


_VERIFIED_RE = re.compile(r"^Verified using (v2|v3|v3\.1) scheme \([^)]*\): true$", re.M)
# "Signer #1 certificate SHA-256 digest: ..." and, for v3.1 key rotation,
# "Signer (minSdkVersion=33, maxSdkVersion=...) certificate SHA-256 digest: ...".
# "Source Stamp Signer ..." lines don't start with "Signer" and aren't APK signers.
_SIGNER_RE = re.compile(r"^Signer[^\n:]* certificate SHA-256 digest: ?([0-9A-Fa-f]{64})\s*$", re.M)


def verified_signer_sha256s(path):
    """Cryptographically verify the APK with apksigner; return the verified signers.

    Raises ApkError unless apksigner verifies the APK, it has a valid v2 or v3
    signature, and at least one signer certificate was reported.
    """
    try:
        proc = subprocess.run(
            [find_apksigner(), "verify", "--verbose", "--print-certs", os.path.abspath(path)],
            capture_output=True, text=True, timeout=300,
        )
    except (OSError, subprocess.SubprocessError) as e:
        raise ApkError(f"apksigner could not run: {e}") from e
    out = proc.stdout
    if proc.returncode != 0 or not re.search(r"^Verifies$", out, re.M):
        reason = (proc.stderr or out).strip().splitlines()
        raise ApkError("apksigner rejected the signature: " + " | ".join(reason[:5]))
    if not _VERIFIED_RE.search(out):
        raise ApkError("apksigner didn't verify a v2 or v3 signature")
    signers = sorted({d.lower() for d in _SIGNER_RE.findall(out)})
    if not signers:
        shown = [line.strip() for line in out.splitlines() if "SHA-256" in line or "Signer" in line]
        shown = shown or [line.strip() for line in out.splitlines()[:12]]
        raise ApkError("apksigner reported no signer certificates: " + " | ".join(shown[:8]))
    return signers


if __name__ == "__main__":
    status = 0
    for p in sys.argv[1:]:
        try:
            for fp in signer_sha256s(p):
                print(f"{fp}  {p}")
        except (ApkError, OSError) as e:
            print(f"ERROR {p}: {e}", file=sys.stderr)
            status = 1
    sys.exit(status)
