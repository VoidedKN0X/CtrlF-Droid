"""Check a downloaded release APK and add it to the F-Droid repo.

    python scripts/add_apk.py <owner/repo> <apk> <release-notes.md> <repo dir>

The APK is only added if all of these hold, otherwise this exits non-zero and
the workflow stops before anything is signed or published:
  * its signatures verify with `apksigner verify` (Google's verifier: checks
    every v1/v2/v3/v3.1 signature and v3 key-rotation lineage), with a valid v2
    or v3 signature, and every signer apksigner verified has its SHA-256 listed
    in that listing's AllowedAPKSigningKeys,
  * every certificate in the v2/v3/v3.1 signing blocks, read independently by
    apk_signers.py (which also rejects malformed or duplicate blocks), is
    listed there too,
  * its package name has a listing in metadata/<package>.yml,
  * that listing's SourceCode is the GitHub repo the APK was downloaded from
    (so one app's release can't ship an APK for another app).
`fdroid update` then verifies the signatures with the same apksigner and checks
AllowedAPKSigningKeys again before signing the index.
The APK is saved as <package>_<versionCode>.apk, never under the asset's name.
"""
import re
import shutil
import sys
from pathlib import Path

import yaml

try:  # androguard 4.x
    from androguard.core.apk import APK
except ImportError:  # androguard 3.x
    from androguard.core.bytecodes.apk import APK

from apk_signers import ApkError, signer_sha256s, verified_signer_sha256s
from whats_new import PACKAGE_RE, write as write_whats_new

ROOT = Path(__file__).resolve().parent.parent
REPO_RE = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(msg: str) -> None:
    print(f"::error::{msg}")
    sys.exit(1)


def main() -> None:
    gh_repo, apk_path, notes_path, repo_dir = sys.argv[1:5]
    if not REPO_RE.match(gh_repo):
        fail(f"Bad repo name {gh_repo!r} in apps.txt")

    try:
        signers = signer_sha256s(apk_path)
    except (ApkError, OSError) as e:
        fail(f"{gh_repo}: {Path(apk_path).name} has no usable v2/v3 signature ({e})")
    try:
        verified = verified_signer_sha256s(apk_path)
    except ApkError as e:
        fail(f"{gh_repo}: {Path(apk_path).name} failed signature verification ({e})")

    apk = APK(apk_path)
    package = apk.get_package() or ""
    version_code = str(apk.get_androidversion_code() or "")
    if not PACKAGE_RE.match(package):
        fail(f"{gh_repo}: APK has an invalid package name {package!r}")
    if not version_code.isdigit() or int(version_code) < 1:
        fail(f"{gh_repo}: APK has an invalid versionCode {version_code!r}")

    meta_file = ROOT / "metadata" / f"{package}.yml"
    if not meta_file.is_file():
        fail(f"{gh_repo}: no listing metadata/{package}.yml for package {package}")
    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}

    source = str(meta.get("SourceCode", "")).rstrip("/").lower()
    if source != f"https://github.com/{gh_repo}".lower():
        fail(f"{gh_repo}: package {package} belongs to {meta.get('SourceCode')}, not this repo")

    allowed = {str(k).lower() for k in meta.get("AllowedAPKSigningKeys") or []}
    if not allowed or not all(SHA256_RE.match(k) for k in allowed):
        fail(f"{package}: AllowedAPKSigningKeys is missing or malformed in {meta_file.name}")
    unknown = sorted({s for s in signers + verified if s not in allowed})
    if unknown:
        fail(
            f"{gh_repo}: {Path(apk_path).name} is signed by an unexpected certificate "
            f"{', '.join(unknown)} - not publishing. If the app's signing key really "
            f"changed, update AllowedAPKSigningKeys in {meta_file.name}."
        )

    dest = Path(repo_dir) / f"{package}_{version_code}.apk"
    if dest.exists():
        fail(f"{gh_repo}: more than one APK with {package} versionCode {version_code}")
    shutil.move(apk_path, dest)
    print(f"{gh_repo}: {package} {version_code} signed by {', '.join(signers)} -> {dest}")

    try:
        write_whats_new(package, int(version_code), notes_path)
    except Exception as e:  # "What's new" is optional; never block the update on it
        print(f"::warning::Couldn't add What's new for {gh_repo}: {e}")


if __name__ == "__main__":
    main()
