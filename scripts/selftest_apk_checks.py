"""Prove on every run that the APK checks reject forged APKs, before anything is signed.

    python scripts/selftest_apk_checks.py <a good, already checked APK> <scratch dir>

Makes broken copies of a real release APK in <scratch dir> and exits non-zero
unless each one is rejected by the check responsible for it (apksigner for the
changed contents, apk_signers.py for the structural tricks):
  * one byte of the signed contents changed (signature no longer matches),
  * the signing block stripped, leaving no v2/v3 signature,
  * a second copy of the signing block's first entry appended (ambiguous APK),
  * a fake ZIP end record hidden after the real one.
"""
import struct
import sys
from pathlib import Path

from apk_signers import MAGIC, ApkError, signer_sha256s, verified_signer_sha256s


def layout(data):
    eocd = len(data) - 22
    assert data[eocd : eocd + 4] == b"PK\x05\x06", "self-test needs an APK without a ZIP comment"
    cd_size, cd_off = struct.unpack_from("<II", data, eocd + 12)
    block_size = struct.unpack_from("<Q", data, cd_off - 24)[0]
    return eocd, cd_off, cd_off - block_size - 8


def set_cd_offset(data, value):
    out = bytearray(data)
    struct.pack_into("<I", out, len(out) - 22 + 16, value)
    return bytes(out)


def forgeries(data):
    eocd, cd_off, start = layout(data)

    tampered = bytearray(data)
    tampered[start // 2] ^= 0x01
    yield "one byte of the contents changed", bytes(tampered)

    yield "signing block stripped", set_cd_offset(data[:start] + data[cd_off:], start)

    block = data[start:cd_off]
    pairs = block[8:-24]
    (n,) = struct.unpack_from("<Q", pairs, 0)
    extra = pairs[: 8 + n]
    size = len(block) - 8 + len(extra)
    new_block = struct.pack("<Q", size) + pairs + extra + struct.pack("<Q", size) + MAGIC
    yield "duplicate signing block entry", set_cd_offset(
        data[:start] + new_block + data[cd_off:], cd_off + len(extra)
    )

    fake = bytearray(data[eocd:])
    struct.pack_into("<I", fake, 16, 0)  # points at the start of the file
    with_comment = bytearray(data)
    struct.pack_into("<H", with_comment, eocd + 20, len(fake))
    yield "fake ZIP end record in the comment", bytes(with_comment) + bytes(fake)


def main():
    good, scratch = Path(sys.argv[1]), Path(sys.argv[2])
    scratch.mkdir(parents=True, exist_ok=True)
    data = good.read_bytes()
    if not signer_sha256s(good) or not verified_signer_sha256s(good):
        sys.exit("::error::self-test: the good APK didn't pass")
    failed = False
    for i, (name, forged) in enumerate(forgeries(data)):
        path = scratch / f"forged-{i}.apk"
        path.write_bytes(forged)
        rejected_by = []
        for label, check in (("parser", signer_sha256s), ("apksigner", verified_signer_sha256s)):
            try:
                check(path)
            except ApkError:
                rejected_by.append(label)
        path.unlink()
        # An APK is only published if both checks pass. apksigner must catch the
        # changed contents (that proves signatures are really verified); the
        # parser must catch the structural tricks (apksigner itself accepts some
        # of them, e.g. it just uses the first of two duplicate blocks).
        needed = "apksigner" if name == "one byte of the contents changed" else "parser"
        ok = needed in rejected_by
        line = f"{name}: rejected by {', '.join(rejected_by) or 'nothing'}"
        print(f"ok   {line}" if ok else f"::error::self-test FAIL {line} (the {needed} check should reject it)")
        failed |= not ok
    if failed:
        sys.exit("::error::self-test: a forged APK got through the checks; not publishing")
    print("Self-test passed: forged APKs are rejected")


if __name__ == "__main__":
    main()
