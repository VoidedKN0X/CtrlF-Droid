"""Turn an app's GitHub release notes into F-Droid "What's new" text.

    python scripts/whats_new.py <apk> <release-notes.md>

Writes metadata/<app id>/en-US/changelogs/<versionCode>.txt, which `fdroid update`
shows as "What's new" for that version in F-Droid, Droid-ify and Neo Store.
"""
import pathlib
import re
import sys

try:  # androguard 4.x
    from androguard.core.apk import APK
except ImportError:  # androguard 3.x
    from androguard.core.bytecodes.apk import APK

LIMIT = 500  # F-Droid's recommended maximum for a changelog


def plain(markdown: str) -> str:
    lines = []
    for line in markdown.splitlines():
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


def main() -> None:
    apk_path, notes_path = sys.argv[1], sys.argv[2]
    apk = APK(apk_path)
    notes = plain(pathlib.Path(notes_path).read_text(encoding="utf-8"))
    if not notes:
        return
    out = pathlib.Path("metadata") / apk.get_package() / "en-US" / "changelogs" / f"{apk.get_androidversion_code()}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(notes + "\n", encoding="utf-8")
    print(f"{out}:\n{notes}\n")


if __name__ == "__main__":
    main()
