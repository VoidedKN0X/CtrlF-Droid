"""Check apps.txt and every store listing before any APK is downloaded.

    python scripts/check_metadata.py [repo root]

Runs first in the update workflow and reports every problem it finds, each as
its own error, so one typo in a listing is named straight away. It only reads
files in this repo and needs nothing but PyYAML (already installed with the
F-Droid tools). It exits non-zero unless all of these hold:
  * every line in apps.txt is one owner/repo, and no app is listed twice,
  * every metadata/<package>.yml is named after a valid package name, is valid
    YAML and has the fields the workflow relies on: Name and Summary (one line
    of text each), SourceCode (https://github.com/<owner>/<repo>) and
    AllowedAPKSigningKeys (one or more SHA-256 fingerprints),
  * no two listings point at the same SourceCode repo,
  * every app in apps.txt has a listing.
A listing whose app is not in apps.txt is only a warning: that is how an app is
taken out of the repo.
add_apk.py and `fdroid update` still do the real checks on every APK afterwards.
"""
import re
import sys
from pathlib import Path

import yaml

REPO_RE = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SOURCE_RE = re.compile(r"^https://github\.com/([A-Za-z0-9-]+/[A-Za-z0-9._-]+?)/?$")


def annotate(text: str) -> str:
    """Make text safe to print inside a GitHub Actions ::error:: or ::warning:: line."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def read_apps(apps_file: Path, errors: list) -> dict:
    """The owner/repo lines of apps.txt in file order: lower-cased name -> name as written."""
    apps = {}
    for number, line in enumerate(apps_file.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):  # the same lines the workflow skips
            continue
        line = line.strip()  # the workflow's `read` drops surrounding spaces too
        if not REPO_RE.match(line):
            errors.append(f"apps.txt line {number}: {line!r} is not an owner/repo name")
        elif line.lower() in apps:
            errors.append(f"apps.txt line {number}: {line} is listed twice")
        else:
            apps[line.lower()] = line
    return apps


def check_listing(meta_file: Path, errors: list):
    """Check one metadata/<package>.yml. Returns its SourceCode owner/repo, or None."""
    name = meta_file.name
    if not PACKAGE_RE.match(meta_file.stem):
        errors.append(f"metadata/{name}: the file name is not a valid package name")
    try:
        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        errors.append(
            f"metadata/{name}: not valid YAML ({' '.join(str(e).split())}). "
            "A value with a colon in it needs quotes around it."
        )
        return None
    if not isinstance(meta, dict):
        errors.append(f"metadata/{name}: expected a list of 'Field: value' lines")
        return None

    for field in ("Name", "Summary"):
        value = meta.get(field)
        if not isinstance(value, str) or not value.strip() or "\n" in value.strip():
            errors.append(f"metadata/{name}: {field} must be one line of text")

    keys = meta.get("AllowedAPKSigningKeys")
    if not isinstance(keys, list) or not keys or not all(SHA256_RE.match(str(k)) for k in keys):
        errors.append(
            f"metadata/{name}: AllowedAPKSigningKeys must list the SHA-256 "
            "(64 hex characters) of the app's release certificate"
        )

    source = meta.get("SourceCode")
    match = SOURCE_RE.match(source) if isinstance(source, str) else None
    if not match:
        errors.append(f"metadata/{name}: SourceCode must be https://github.com/<owner>/<repo>")
        return None
    return match.group(1)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    errors, warnings = [], []

    apps = read_apps(root / "apps.txt", errors)
    if not apps:
        errors.append("apps.txt lists no apps")

    listings = {}  # SourceCode owner/repo, lower-cased -> listing file name
    files = sorted((root / "metadata").glob("*.yml"))
    for meta_file in files:
        source = check_listing(meta_file, errors)
        if source is None:
            continue
        if source.lower() in listings:
            errors.append(
                f"metadata/{meta_file.name}: same SourceCode as metadata/{listings[source.lower()]}"
            )
            continue
        listings[source.lower()] = meta_file.name
        if source.lower() not in apps:
            warnings.append(
                f"metadata/{meta_file.name}: {source} is not in apps.txt, so this app is not in the repo"
            )

    for key, app in apps.items():
        if key not in listings:
            errors.append(
                f"apps.txt: {app} has no listing (no valid metadata/<package>.yml "
                f"with SourceCode https://github.com/{app})"
            )

    for message in warnings:
        print(f"::warning::{annotate(message)}")
    for message in errors:
        print(f"::error::{annotate(message)}")
    if errors:
        print(f"{len(errors)} problem(s) in apps.txt or metadata/. Nothing was downloaded, signed or published.")
        return 1
    print(f"{len(apps)} apps in apps.txt, {len(files)} listings: all fine.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
