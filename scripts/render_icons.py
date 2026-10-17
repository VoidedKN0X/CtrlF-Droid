"""Turn each app's adaptive launcher icon (vector XML) into an SVG store icon.

Usage: python scripts/render_icons.py <app source checkout> <output.svg>

Android adaptive icons are a background and a foreground on a 108x108 canvas,
of which launchers show the middle 72x72. This draws both layers, crops to that
middle area and rounds the corners, so the result looks like the home-screen icon.
"""
import re
import sys
from xml.sax.saxutils import quoteattr
import xml.etree.ElementTree as ET
from pathlib import Path

A = "{http://schemas.android.com/apk/res/android}"
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
HEX_RE = re.compile(r"^[0-9A-Fa-f]{8}$")
AAPT = "{http://schemas.android.com/aapt}"

app_dir = Path(sys.argv[1])
out_file = Path(sys.argv[2])
res = app_dir / "app" / "src" / "main" / "res"

# ---- resources -------------------------------------------------------------

colors = {}
for values in sorted(res.glob("values*/")):
    if "night" in values.name and colors:
        continue
    for xml in values.glob("*.xml"):
        try:
            root = ET.parse(xml).getroot()
        except ET.ParseError:
            continue
        for c in root.iter("color"):
            colors.setdefault(c.get("name"), (c.text or "").strip())

ANDROID_COLORS = {"white": "#FFFFFFFF", "black": "#FF000000", "transparent": "#00000000"}


def resolve_color(value, depth=0):
    """Return (#rrggbb, alpha 0-1) for an Android colour value or reference."""
    if value is None or depth > 5:
        return None
    value = value.strip()
    if value.startswith("@android:color/"):
        value = ANDROID_COLORS.get(value.split("/", 1)[1], "#FF000000")
    elif value.startswith("@color/"):
        return resolve_color(colors.get(value.split("/", 1)[1]), depth + 1)
    if not value.startswith("#"):
        return None
    h = value[1:]
    if len(h) == 3:
        h = "F" + h
    if len(h) == 4:
        h = "".join(ch * 2 for ch in h)
    if len(h) == 6:
        h = "FF" + h
    if not HEX_RE.match(h):  # only plain hex colours reach the SVG
        return None
    alpha = int(h[0:2], 16) / 255
    return "#" + h[2:].lower(), alpha


def find_drawable(name):
    for folder in sorted(res.glob("drawable*/")):
        f = folder / f"{name}.xml"
        if f.exists():
            return f
    return None


# ---- vector drawable -> svg ------------------------------------------------

defs = []
counter = [0]


def num(el, attr, default=0.0):
    v = el.get(A + attr)
    return float(v) if v is not None else default


def gradient(el):
    counter[0] += 1
    gid = f"g{counter[0]}"
    kind = el.get(A + "type", "linear")
    stops = []
    for item in el.findall("item"):
        c = resolve_color(item.get(A + "color")) or ("#000000", 1)
        stops.append((float(item.get(A + "offset", 0)), c))
    if not stops:
        names = [("startColor", 0), ("centerColor", 0.5), ("endColor", 1)]
        for attr, off in names:
            c = resolve_color(el.get(A + attr))
            if c:
                stops.append((off, c))
    stop_xml = "".join(
        f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a:.3f}"/>' for o, (c, a) in stops
    )
    if kind == "radial":
        defs.append(
            f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'cx="{num(el, "centerX")}" cy="{num(el, "centerY")}" r="{num(el, "gradientRadius", 1)}">'
            f"{stop_xml}</radialGradient>"
        )
    elif kind == "sweep":  # no SVG equivalent; use the first colour
        return stops[0][1][0] if stops else "#000000", stops[0][1][1] if stops else 1
    else:
        defs.append(
            f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{num(el, "startX")}" y1="{num(el, "startY")}" x2="{num(el, "endX")}" y2="{num(el, "endY")}">'
            f"{stop_xml}</linearGradient>"
        )
    return f"url(#{gid})", 1.0


def paint(el, attr):
    """Paint for fillColor / strokeColor: plain colour or an aapt:attr gradient."""
    for inline in el.findall(AAPT + "attr"):
        if inline.get("name") == "android:" + attr:
            g = inline.find("gradient")
            if g is not None:
                return gradient(g)
    c = resolve_color(el.get(A + attr))
    return c if c else None


def convert(el):
    tag = el.tag
    if tag == "group":
        px, py = num(el, "pivotX"), num(el, "pivotY")
        tx, ty = num(el, "translateX"), num(el, "translateY")
        sx, sy = num(el, "scaleX", 1), num(el, "scaleY", 1)
        rot = num(el, "rotation")
        t = f"translate({tx + px} {ty + py}) rotate({rot}) scale({sx} {sy}) translate({-px} {-py})"
        inner = []
        clip = None
        for child in el:
            if child.tag == "clip-path":
                counter[0] += 1
                clip = f"c{counter[0]}"
                defs.append(f'<clipPath id="{clip}"><path d={quoteattr(child.get(A + "pathData") or "")}/></clipPath>')
                continue
            s = convert(child)
            if s:
                inner.append(f'<g clip-path="url(#{clip})">{s}</g>' if clip else s)
        return f'<g transform="{t}">{"".join(inner)}</g>'
    if tag == "path":
        d = el.get(A + "pathData")
        if not d:
            return ""
        attrs = [f"d={quoteattr(d)}"]
        fill = paint(el, "fillColor")
        if fill:
            attrs.append(f'fill="{fill[0]}" fill-opacity="{fill[1] * num(el, "fillAlpha", 1):.3f}"')
        else:
            attrs.append('fill="none"')
        if el.get(A + "fillType") == "evenOdd":
            attrs.append('fill-rule="evenodd"')
        stroke = paint(el, "strokeColor")
        width = num(el, "strokeWidth", 0)
        if stroke and width > 0:
            attrs.append(
                f'stroke="{stroke[0]}" stroke-opacity="{stroke[1] * num(el, "strokeAlpha", 1):.3f}" '
                f'stroke-width="{width}"'
            )
            cap = el.get(A + "strokeLineCap")
            join = el.get(A + "strokeLineJoin")
            if cap:
                attrs.append(f"stroke-linecap={quoteattr(cap)}")
            if join:
                attrs.append(f"stroke-linejoin={quoteattr(join)}")
            if el.get(A + "strokeMiterLimit"):
                attrs.append(f"stroke-miterlimit={quoteattr(el.get(A + 'strokeMiterLimit'))}")
        return f'<path {" ".join(attrs)}/>'
    return ""


def layer(drawable_ref):
    """SVG for one adaptive-icon layer, scaled onto the 108x108 canvas."""
    if not drawable_ref:
        return ""
    if drawable_ref.startswith("@color/") or drawable_ref.startswith("#"):
        c = resolve_color(drawable_ref) or ("#000000", 1)
        return f'<rect width="108" height="108" fill="{c[0]}" fill-opacity="{c[1]:.3f}"/>'
    f = find_drawable(drawable_ref.split("/", 1)[1])
    if not f:
        raise SystemExit(f"Can't find {drawable_ref}")
    root = ET.parse(f).getroot()
    if root.tag == "shape":  # simple solid-colour shape drawable
        solid = root.find("solid")
        c = resolve_color(solid.get(A + "color")) if solid is not None else ("#000000", 1)
        return f'<rect width="108" height="108" fill="{c[0]}" fill-opacity="{c[1]:.3f}"/>'
    if root.tag != "vector":
        raise SystemExit(f"Unsupported drawable type <{root.tag}> in {f}")
    vw, vh = num(root, "viewportWidth", 108), num(root, "viewportHeight", 108)
    body = "".join(convert(child) for child in root)
    return f'<g transform="scale({108 / vw} {108 / vh})">{body}</g>'


launcher = None
for folder in sorted(res.glob("mipmap-anydpi*/")):
    if (folder / "ic_launcher.xml").exists():
        launcher = folder / "ic_launcher.xml"
        break
if not launcher:
    raise SystemExit("No adaptive ic_launcher.xml found")

icon = ET.parse(launcher).getroot()
bg = icon.find("background")
fg = icon.find("foreground")
layers = layer(bg.get(A + "drawable") if bg is not None else None) + layer(
    fg.get(A + "drawable") if fg is not None else None
)

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="18 18 72 72">'
    f'<defs><clipPath id="mask"><rect x="18" y="18" width="72" height="72" rx="16"/></clipPath>{"".join(defs)}</defs>'
    f'<g clip-path="url(#mask)">{layers}</g></svg>'
)
out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text(svg)

gradle = (app_dir / "app" / "build.gradle.kts").read_text()
m = re.search(r'applicationId\s*=\s*"([^"]+)"', gradle)
package = m.group(1) if m else ""
if not PACKAGE_RE.match(package):  # used as a folder name by the workflow
    raise SystemExit(f"No valid applicationId in {app_dir}/app/build.gradle.kts")
print(package)
