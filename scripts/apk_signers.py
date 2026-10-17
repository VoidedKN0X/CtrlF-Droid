"""Read the signing certificates of an APK from its v2/v3 APK Signing Block.

Pure Python (standard library only), so it doesn't trust androguard or any other
APK parser. Only the certificates are read; the signatures themselves are
verified by `fdroid update` (apksigner), which also enforces AllowedAPKSigningKeys.

    python scripts/apk_signers.py <apk>...   # prints "<sha256>  <apk>" per signer
"""
import hashlib
import struct
import sys

V2_ID = 0x7109871A
V3_ID = 0xF05368C0
V31_ID = 0x1B93AD61
MAGIC = b"APK Sig Block 42"


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


def _signing_block(f):
    f.seek(0, 2)
    size = f.tell()
    tail_len = min(size, 65535 + 22)
    f.seek(size - tail_len)
    tail = f.read(tail_len)
    eocd = tail.rfind(b"PK\x05\x06")
    if eocd < 0 or eocd + 22 > len(tail):
        raise ApkError("not a ZIP file (no end of central directory)")
    (cd_offset,) = struct.unpack_from("<I", tail, eocd + 16)
    if cd_offset < 32 or cd_offset > size:
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
    if struct.unpack_from("<Q", block, 0)[0] != block_size:
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
        pairs[pid] = block[off + 12 : off + 8 + n]
        off += 8 + n
    return pairs


def _scheme_certs(value):
    """First certificate of every signer in a v2/v3 signature scheme block."""
    certs = []
    signers, _ = _lp(value, 0)
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

    Raises ApkError if the APK has no v2+ signature.
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
