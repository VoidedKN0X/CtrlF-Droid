"""Turn an app's GitHub release notes into F-Droid "What's new" text.

    python scripts/whats_new.py <package> <versionCode> <release-notes.md>

Writes metadata/<package>/en-US/changelogs/<versionCode>.txt, which `fdroid update`
shows as "What's new" for that version in F-Droid, Droid-ify and Neo Store.
The release notes are treated as untrusted text: HTML, control characters and
invisible direction overrides are removed, and the length is capped.
"""
import pathlib
import re
import sys

LIMIT = 500  # F-Droid's recommended maximum for a changelog
MAX_INPUT = 64 * 1024  # ignore anything past this; release notes are never this long

PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
# C0/C1 control characters (except tab and newline), bidi overrides/isolates,
# zero-width characters and other invisible format characters.
INVISIBLE_RE = re.compile(
    "[\x00-\x08\x0b-\x1f\x7f-\x9f​-‏‪-‮⁠-⁩﻿￹-￻]"
)


def clean(text: str) -> str:
    text = text[:MAX_INPUT].replace("\r\n", "\n").replace("\r", "\n")
    text = INVISIBLE_RE.sub("", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)       # HTML comments
    text = re.sub(r"</?[A-Za-z][^<>]*>", "", text)            # HTML tags
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)     # images -> alt text
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)      # links -> link text
    return text


def plain(markdown: str) -> str:
    lines = []
    for line in clean(markdown).splitlines():
        if line.startswith("**Full diff:**"):
            continue
        line = re.sub(r"^#+\s*", "", line)            # headings
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)  # bold
        line = re.sub(r"`([^`]*)`", r"\1", line)      # code
        line = re.sub(r"^(\s*)[-*] ", r"\1• ", line)  # bullets
        if line.strip() in ("What's new", "First release") and not lines:
            continue                                  # the heading adds nothing in a "What's new" box
        lines.append(line.rstrip())
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) > LIMIT:
        cut = text[: LIMIT - 1].rsplit("\n", 1)[0].rstrip()
        text = cut + "\n…"
    return text


def write(package: str, version_code: int, notes_path: str) -> None:
    if not PACKAGE_RE.match(package):
        raise SystemExit(f"Refusing unsafe package name {package!r}")
    version_code = int(version_code)
    if version_code < 1:
        raise SystemExit(f"Refusing bad versionCode {version_code!r}")
    try:
        raw = pathlib.Path(notes_path).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return
    notes = plain(raw)
    if not notes:
        return
    out = pathlib.Path("metadata") / package / "en-US" / "changelogs" / f"{version_code}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(notes + "\n", encoding="utf-8")
    print(f"{out}:\n{notes}\n")


if __name__ == "__main__":
    write(sys.argv[1], int(sys.argv[2]), sys.argv[3])
