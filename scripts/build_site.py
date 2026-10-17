"""Build the CtrlF-Droid landing page into _site/ next to the generated F-Droid repo.

Usage: python scripts/build_site.py <FINGERPRINT>
Reads repo/index-v1.json (written by `fdroid update`) and metadata/*.yml.
"""
import html
import json
import shutil
import sys
from pathlib import Path

import qrcode
import qrcode.image.svg
import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "repo"
SITE = ROOT / "_site"
REPO_URL = "https://voidedkn0x.github.io/CtrlF-Droid/repo"

fingerprint = sys.argv[1].replace(":", "").strip().upper()
add_https = f"{REPO_URL}?fingerprint={fingerprint}"
add_app = add_https.replace("https://", "fdroidrepos://", 1)

index = json.loads((REPO / "index-v1.json").read_text())
packages = index.get("packages", {})
icons = {a["packageName"]: a.get("icon") for a in index.get("apps", [])}


def icon_path(pkg):
    name = icons.get(pkg)
    if not name:
        return None
    for folder in ("icons-640", "icons-480", "icons-320", "icons"):
        if (REPO / folder / name).exists():
            return f"repo/{folder}/{name}"
    return None


cards = []
for meta_file in sorted((ROOT / "metadata").glob("*.yml")):
    pkg = meta_file.stem
    if pkg not in packages:
        continue
    meta = yaml.safe_load(meta_file.read_text())
    latest = max(packages[pkg], key=lambda p: p.get("versionCode", 0))
    icon = icon_path(pkg)
    icon_html = (
        f'<img src="{icon}" alt="" width="56" height="56">' if icon
        else f'<div class="ph">{html.escape(meta["Name"][0])}</div>'
    )
    cards.append(f"""
      <a class="card" href="{html.escape(meta['SourceCode'])}">
        {icon_html}
        <div>
          <h3>{html.escape(meta['Name'])} <span>{html.escape(latest.get('versionName', ''))}</span></h3>
          <p>{html.escape(meta['Summary'])}</p>
        </div>
      </a>""")

qr = qrcode.make(add_https, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
qr_svg = qr.to_string(encoding="unicode")

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CtrlF-Droid</title>
<link rel="icon" href="repo/icons/icon.png">
<style>
  :root {{ --bg:#f6f4fb; --fg:#1b1530; --muted:#5d5675; --card:#fff; --line:#e4dff2; --accent:#6b45f2; --accent-fg:#fff; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0f0c19; --fg:#ece8f8; --muted:#a39cbd; --card:#191428; --line:#2a2340; --accent:#8f70ff; --accent-fg:#0f0c19; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  main {{ max-width:880px; margin:0 auto; padding:40px 16px 64px; }}
  header {{ display:flex; gap:20px; align-items:center; }}
  header img {{ width:72px; height:72px; border-radius:18px; }}
  h1 {{ margin:0; font-size:2rem; }}
  .lead {{ color:var(--muted); margin:4px 0 0; }}
  .add {{ display:grid; grid-template-columns:1fr auto; gap:24px; align-items:center; background:var(--card); border:1px solid var(--line); border-radius:20px; padding:24px; margin:32px 0; }}
  .add h2 {{ margin:0 0 8px; font-size:1.2rem; }}
  .add ol {{ margin:0 0 16px; padding-left:20px; color:var(--muted); }}
  .btn {{ display:inline-block; background:var(--accent); color:var(--accent-fg); text-decoration:none; font-weight:600; padding:12px 20px; border-radius:999px; }}
  .qr {{ background:#fff; border-radius:12px; padding:8px; width:180px; }}
  .qr svg {{ display:block; width:100%; height:auto; }}
  code {{ font-size:.8rem; word-break:break-all; color:var(--muted); }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:12px; }}
  .card {{ display:flex; gap:14px; align-items:center; background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px; color:inherit; text-decoration:none; }}
  .card:hover {{ border-color:var(--accent); }}
  .card img, .ph {{ border-radius:14px; flex:none; }}
  .ph {{ width:56px; height:56px; display:grid; place-items:center; background:var(--accent); color:var(--accent-fg); font-weight:700; font-size:1.4rem; }}
  .card h3 {{ margin:0; font-size:1rem; }}
  .card h3 span {{ font-weight:400; color:var(--muted); font-size:.85rem; }}
  .card p {{ margin:2px 0 0; color:var(--muted); font-size:.9rem; }}
  footer {{ margin-top:40px; color:var(--muted); font-size:.9rem; }}
  footer a {{ color:var(--accent); }}
  @media (max-width:600px) {{ .add {{ grid-template-columns:1fr; }} .qr {{ width:160px; }} }}
</style>
</head>
<body>
<main>
  <header>
    <img src="repo/icons/icon.png" alt="">
    <div>
      <h1>CtrlF-Droid</h1>
      <p class="lead">The VKNXWorks Ctrl series in one F-Droid repo. Free, open source, updated automatically.</p>
    </div>
  </header>

  <section class="add">
    <div>
      <h2>Add the repo</h2>
      <ol>
        <li>Install <a href="https://f-droid.org">F-Droid</a>, Droid-ify or Neo Store.</li>
        <li>On your phone, tap the button. Or scan the QR code from the app's repo settings.</li>
        <li>All Ctrl apps appear in your store, with automatic updates.</li>
      </ol>
      <a class="btn" href="{html.escape(add_app)}">Add to F-Droid</a>
      <p><code>{html.escape(add_https)}</code></p>
    </div>
    <div class="qr">{qr_svg}</div>
  </section>

  <h2>Apps</h2>
  <div class="grid">{''.join(cards)}
  </div>

  <footer>
    Made by VKNXWorks · <a href="https://github.com/sponsors/VoidedKN0X">Support on GitHub Sponsors</a> ·
    <a href="https://github.com/VoidedKN0X/CtrlF-Droid">Repo source</a>
  </footer>
</main>
</body>
</html>
"""

if SITE.exists():
    shutil.rmtree(SITE)
SITE.mkdir()
shutil.copytree(REPO, SITE / "repo")
(SITE / "index.html").write_text(page)
(SITE / "fingerprint.txt").write_text(fingerprint + "\n")
(SITE / ".nojekyll").write_text("")
print(f"Site built with {len(cards)} apps. Fingerprint {fingerprint}")
