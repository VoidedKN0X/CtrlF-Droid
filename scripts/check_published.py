"""Stop an update that would make a published app disappear from the repo.

    python scripts/check_published.py fetch <published.json> [index url]
    python scripts/check_published.py apks  <published.json> <repo dir>
    python scripts/check_published.py index <published.json> <new index-v1.json>

`fetch` downloads the index-v1.json that is live right now (repo_url in
config.yml) to <published.json>. It tries a few times and exits non-zero if it
still can't get a readable index, so the run stops and the current repo stays
live. Only a plain "not found" (HTTP 404: nothing was ever published) is
accepted; the checks below are then skipped with a warning.

`apks` (before the signing key is touched) and `index` (on the index that
`fdroid update` wrote) compare the apps about to be published with the live
ones, and exit non-zero if a live app is missing. An app may only go missing
when it was taken out on purpose: its repo is no longer in apps.txt, or its
metadata/<package>.yml is gone.

The live index is only used as a list of package names to make this run
stricter. It is not trusted for anything else: its signature is not checked
here, and a wrong or tampered copy can only stop a run, never add or change
what gets published.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
APK_NAME_RE = re.compile(r"^(?P<package>.+)_(?P<code>[0-9]+)\.apk$")
SOURCE_RE = re.compile(r"^https://github\.com/([A-Za-z0-9-]+/[A-Za-z0-9._-]+?)/?$")
TRIES = 4
MAX_BYTES = 32 * 1024 * 1024  # the real index is well under 1 MB
NOTHING_PUBLISHED = {"nothing_published": True}


def annotate(text: str) -> str:
    """Make text safe to print inside a GitHub Actions ::error:: or ::warning:: line."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def fail(message: str) -> None:
    print(f"::error::{annotate(message)}")
    sys.exit(1)


def packages_of(index, what: str) -> set:
    """Package names that have at least one APK in an index-v1.json document."""
    packages = index.get("packages") if isinstance(index, dict) else None
    if not isinstance(packages, dict):
        fail(f"{what} is not an F-Droid index (no package list)")
    names = {name for name, versions in packages.items() if versions}
    bad = sorted(n for n in names if not isinstance(n, str) or not PACKAGE_RE.match(n))
    if bad:
        fail(f"{what} has an invalid package name {bad[0]!r}")
    return names


def fetch(out_path: str, url: str = "") -> None:
    if not url:
        config = yaml.safe_load((ROOT / "config.yml").read_text(encoding="utf-8")) or {}
        url = str(config.get("repo_url", "")).rstrip("/") + "/index-v1.json"
    if not url.startswith(("https://", "http://")):
        fail(f"Can't fetch the published index from {url!r}")
    problem = ""
    for attempt in range(1, TRIES + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                fail(f"The published index at {url} is unexpectedly large")
            published = sorted(packages_of(json.loads(data), "The published index"))
            Path(out_path).write_bytes(data)
            print(f"Published index: {len(published)} apps ({url})")
            return
        except urllib.error.HTTPError as e:
            if e.code == 404:
                Path(out_path).write_text(json.dumps(NOTHING_PUBLISHED), encoding="utf-8")
                print(
                    f"::warning::No published index at {annotate(url)} (HTTP 404). Treating this "
                    "as a first publish: the check for disappearing apps is skipped."
                )
                return
            problem = f"HTTP {e.code}"
        except (OSError, ValueError) as e:  # network errors, timeouts, bad JSON
            problem = " ".join(str(e).split()) or type(e).__name__
        if attempt < TRIES:
            print(f"Attempt {attempt} of {TRIES} failed ({problem}); trying again in {attempt * 15}s")
            time.sleep(attempt * 15)
    fail(
        f"Couldn't read the published index at {url} after {TRIES} attempts ({problem}). "
        "Nothing was signed or published; the current repo stays live."
    )


def load_published(path: str):
    """Package names in the fetched live index, or None when nothing is published yet."""
    try:
        published = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail(f"Can't read the fetched published index {path} ({e}); run the fetch step first")
    if published == NOTHING_PUBLISHED:
        return None
    return packages_of(published, "The published index")


def apps_txt() -> set:
    lines = (ROOT / "apps.txt").read_text(encoding="utf-8").splitlines()
    return {line.strip().lower() for line in lines if line.strip() and not line.startswith("#")}


def removed_on_purpose(package: str, apps: set) -> str:
    """Why a missing package is fine, or "" when it should still be in the repo."""
    meta_file = ROOT / "metadata" / f"{package}.yml"
    if not meta_file.is_file():
        return f"metadata/{package}.yml is gone"
    try:
        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError):
        return ""
    source = meta.get("SourceCode") if isinstance(meta, dict) else None
    match = SOURCE_RE.match(source) if isinstance(source, str) else None
    if match and match.group(1).lower() not in apps:
        return f"{match.group(1)} is not in apps.txt"
    return ""


def compare(published_path: str, new: set, what: str) -> None:
    published = load_published(published_path)
    if not new:
        fail(f"{what} has no apps; refusing to publish an empty repo")
    if published is None:
        print("::warning::Nothing is published yet, so there is nothing to compare with.")
        return
    apps = apps_txt()
    missing = []
    for package in sorted(published - new):
        reason = removed_on_purpose(package, apps)
        if reason:
            print(f"{package} leaves the repo on purpose: {reason}")
        else:
            missing.append(package)
    for package in missing:
        print(
            f"::error::{package} is in the published repo and still in apps.txt, but {what} "
            "doesn't have it (no release, or no APK in its latest release?). To take an app "
            "out of the repo on purpose, remove its line from apps.txt."
        )
    if missing:
        print(
            f"{len(missing)} published app(s) would disappear. "
            "Nothing was published; the current repo stays live."
        )
        sys.exit(1)
    added = sorted(new - published)
    print(
        f"{what}: {len(new)} apps, none of the {len(published)} published apps is missing"
        + (f"; new: {', '.join(added)}" if added else "")
    )


def apk_packages(repo_dir: str) -> set:
    names = set()
    for apk in sorted(Path(repo_dir).glob("*.apk")):
        match = APK_NAME_RE.match(apk.name)  # add_apk.py saves <package>_<versionCode>.apk
        if not match or not PACKAGE_RE.match(match.group("package")):
            fail(f"Unexpected APK file name {apk.name!r} in {repo_dir}")
        names.add(match.group("package"))
    return names


def main() -> None:
    args = sys.argv[1:]
    if len(args) in (2, 3) and args[0] == "fetch":
        fetch(*args[1:])
    elif len(args) == 3 and args[0] == "apks":
        compare(args[1], apk_packages(args[2]), "the set of checked APKs")
    elif len(args) == 3 and args[0] == "index":
        try:
            index = json.loads(Path(args[2]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            fail(f"Can't read the new index {args[2]} ({e})")
        compare(args[1], packages_of(index, "The new index"), "the new index")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
