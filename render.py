#!/usr/bin/env python3
"""FG Banner Generator v3.3

Commands
    python render.py list                  list projects
    python render.py check [project-id]    validate + measure layout, save nothing
    python render.py all                   render every project
    python render.py <project-id>          render one project
    python render.py icons                 build output/icons.html (icon catalog)

Options
    --template NAME      override the template of every selected project
    --all-templates      render every project in every available template
    --strict             exit with code 1 when layout warnings are found
                         (always on for `check`)

Environment
    FG_CHROMIUM          path to a Chromium/Chrome executable
    FG_BROWSER_ARGS      extra launch args, whitespace separated (e.g. --no-sandbox)
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import mimetypes
import os
import shlex
import shutil
import sys
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from playwright.async_api import async_playwright

try:  # keep ✓ / ⚠ printable on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
PROJECTS_FILE = ROOT / "projects.json"
TEMPLATES_DIR = ROOT / "templates"
ICONS_DIR = TEMPLATES_DIR / "icons"
OUTPUT_DIR = ROOT / "output"

DEFAULT_WIDTH = 1600
DEFAULT_HEIGHT = 700

# Built-in fallback so a missing key in projects.json can never produce an
# empty CSS variable (v3.2.x lost `accent` this way and the `banner` template
# rendered without its accent colour).
DEFAULT_PALETTE = {
    "background_top": "#071B35",
    "background_bottom": "#031126",
    "text_primary": "#F7F9FF",
    "text_secondary": "#B8C6DF",
    "panel_fill": "#0A294A",
    "panel_border": "#2B5C86",
    "panel_glow": "#FF5A3D",
    "accent": "#FF4B1F",
    "accent_secondary": "#FF7A45",
}

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    undefined=StrictUndefined,
)


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #

def load_data() -> dict[str, Any]:
    return json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))


def available_templates() -> list[str]:
    """A template is a `<name>.html` with a matching `<name>.css`."""
    names = []
    for html in sorted(TEMPLATES_DIR.glob("*.html")):
        if (TEMPLATES_DIR / f"{html.stem}.css").exists():
            names.append(html.stem)
    return names


def merged_project(data: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    defaults = dict(data.get("defaults", {}))
    theme_name = project.get("theme", defaults.get("theme", "orange"))
    theme = data.get("themes", {}).get(theme_name, {})

    cfg: dict[str, Any] = {}
    cfg.update(defaults)
    cfg.update(project)

    palette = dict(DEFAULT_PALETTE)
    palette.update(defaults.get("palette", {}))
    palette.update(theme.get("palette", {}))
    palette.update(project.get("palette", {}))
    cfg["palette"] = palette

    cfg.setdefault("template", "banner")
    cfg.setdefault("width", DEFAULT_WIDTH)
    cfg.setdefault("height", DEFAULT_HEIGHT)
    cfg.setdefault("title_prefix", "FG")
    cfg.setdefault("subtitle", "")
    cfg.setdefault("extension_type", "")
    cfg.setdefault("placeholder_logo", "FG")
    cfg.setdefault("logo", "")
    cfg.setdefault("logo_mode", "contain")
    cfg.setdefault("logo_size", None)
    cfg.setdefault("logo_scale", None)
    cfg.setdefault("logo_offset_x", None)
    cfg.setdefault("logo_offset_y", None)
    cfg.setdefault("features", [])
    cfg["features"] = [{"hero": False, **f} for f in cfg["features"]]
    cfg.setdefault("joomla", [])
    cfg.setdefault("badges", [])
    cfg.setdefault("category", {})
    cfg.setdefault("license", "")
    cfg.setdefault("download", "")
    cfg.setdefault("developer", "")
    cfg.setdefault("output", f"{cfg.get('id', 'banner')}.png")
    return cfg


def projects() -> list[dict[str, Any]]:
    data = load_data()
    return [merged_project(data, p) for p in data.get("projects", [])]


def asset_data_uri(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    p = (ROOT / relative_path).resolve()
    if not p.exists():
        return None
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def template_of(project: dict[str, Any], override: str | None) -> str:
    return override or project.get("template", "banner")


# --------------------------------------------------------------------------- #
# Validation (static, before any browser is started)
# --------------------------------------------------------------------------- #

def validate(project: dict[str, Any], template_name: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors abort the render of that project."""
    errors: list[str] = []
    warnings: list[str] = []
    pid = project.get("id", "<no id>")

    for key in ("id", "title"):
        if not project.get(key):
            errors.append(f"{pid}: missing required key '{key}'")

    if template_name not in available_templates():
        errors.append(
            f"{pid}: unknown template '{template_name}' "
            f"(available: {', '.join(available_templates()) or 'none'})"
        )

    feats = project.get("features") or []
    if not feats:
        errors.append(f"{pid}: 'features' is empty")
    for i, f in enumerate(feats, 1):
        for key in ("icon", "heading", "description"):
            if not f.get(key):
                errors.append(f"{pid}: feature #{i} is missing '{key}'")
        icon = f.get("icon")
        if icon and not (ICONS_DIR / f"{icon}.svg").exists():
            errors.append(f"{pid}: feature #{i} icon '{icon}' not found in templates/icons/")

    cat = project.get("category") or {}
    if cat.get("name") and template_name == "jed":
        cicon = cat.get("icon")
        if not cicon:
            errors.append(f"{pid}: category has a name but no 'icon'")
        elif not (ICONS_DIR / f"{cicon}.svg").exists():
            errors.append(f"{pid}: category icon '{cicon}' not found in templates/icons/")

    logo = project.get("logo")
    if logo and not (ROOT / logo).exists():
        warnings.append(f"{pid}: logo '{logo}' not found - placeholder will be used")
    if not logo:
        warnings.append(f"{pid}: no logo set - placeholder will be used")

    if sum(1 for f in feats if f.get("hero")) > 1:
        warnings.append(f"{pid}: more than one feature has hero=true")

    return errors, warnings


def validate_outputs(selected: list[dict[str, Any]], override: str | None,
                     all_templates: bool) -> list[str]:
    """Two projects must not write the same file."""
    seen: dict[tuple[str, str], str] = {}
    errors = []
    for p in selected:
        names = available_templates() if all_templates else [template_of(p, override)]
        for t in names:
            key = (t, p["output"])
            if key in seen:
                errors.append(
                    f"output collision in {t}/: '{p['output']}' used by "
                    f"'{seen[key]}' and '{p['id']}'"
                )
            seen[key] = p["id"]
    return errors


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def render_html(project: dict[str, Any], template_name: str) -> str:
    ctx = dict(project)
    ctx["logo_uri"] = asset_data_uri(project.get("logo"))
    ctx["css_text"] = (TEMPLATES_DIR / f"{template_name}.css").read_text(encoding="utf-8")
    ctx["template_name"] = template_name
    return env.get_template(f"{template_name}.html").render(**ctx)


# Runs in the page: shrink an overflowing title, then measure everything that
# can silently overflow. Returns {issues: [...], shrunk: {from,to}|null}.
FIT_AND_CHECK_JS = """
(size) => {
  const root = document.querySelector('.jed-banner, .banner');
  const issues = [];
  let shrunk = null;
  if (!root) return {issues: ['layout root (.jed-banner / .banner) not found'], shrunk};

  const R = root.getBoundingClientRect();
  if (Math.abs(R.width - size.w) > 1 || Math.abs(R.height - size.h) > 1) {
    issues.push(`layout root is ${Math.round(R.width)}x${Math.round(R.height)} but the ` +
                `project asks for ${size.w}x${size.h} (template size is fixed in CSS)`);
  }

  const h1 = document.querySelector('h1');
  if (h1) {
    const start = parseFloat(getComputedStyle(h1).fontSize);
    let s = start;
    while (h1.scrollWidth > h1.clientWidth + 1 && s > 44) {
      s -= 1;
      h1.style.fontSize = s + 'px';
    }
    if (s !== start) shrunk = {from: start, to: s};
  }

  // subtitle: shrink until it fits on one line (down to 26px)
  let subShrunk = null;
  const subEl = document.querySelector('.subtitle');
  if (subEl) {
    const subLines = () => Math.round(subEl.getBoundingClientRect().height /
                                      parseFloat(getComputedStyle(subEl).lineHeight));
    const start = parseFloat(getComputedStyle(subEl).fontSize);
    let s = start;
    while (subLines() > 1 && s > 26) { s -= 1; subEl.style.fontSize = s + 'px'; }
    if (s !== start) subShrunk = {from: start, to: s};
  }

  const label = el => el.tagName.toLowerCase() +
    (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '');
  const text = el => el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 48);

  document.querySelectorAll('h1, .subtitle, .feature h2, .feature p, .extension-type, .badge')
    .forEach(el => {
      const r = el.getBoundingClientRect();
      if (el.scrollWidth > el.clientWidth + 1)
        issues.push(`${label(el)} is cut off horizontally: "${text(el)}"`);
      if (r.right > R.right - 24 || r.bottom > R.bottom - 24 || r.left < R.left + 8)
        issues.push(`${label(el)} is too close to the banner edge: "${text(el)}"`);
    });

  const sub = document.querySelector('.subtitle');
  if (sub) {
    const lh = parseFloat(getComputedStyle(sub).lineHeight);
    const lines = Math.round(sub.getBoundingClientRect().height / lh);
    if (lines > 1) issues.push(`subtitle wraps to ${lines} lines`);
  }

  const dev = document.querySelector('.developer');
  const feats = document.querySelectorAll('.feature');
  if (dev && feats.length) {
    const last = feats[feats.length - 1].getBoundingClientRect();
    if (last.bottom > dev.getBoundingClientRect().top - 8)
      issues.push('last feature overlaps the "by developer" line');
  }
  return {issues, shrunk, subShrunk};
}
"""


def browser_launch_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    exe = (
        os.environ.get("FG_CHROMIUM")
        or shutil.which("chromium")
        or shutil.which("chromium-browser")
        or shutil.which("google-chrome")
    )
    if exe:
        kwargs["executable_path"] = exe
    extra = os.environ.get("FG_BROWSER_ARGS", "").strip()
    if extra:
        kwargs["args"] = shlex.split(extra)
    return kwargs


async def render_one(browser, project: dict[str, Any], template_name: str,
                     save: bool) -> tuple[Path | None, list[str]]:
    w = int(project.get("width", DEFAULT_WIDTH))
    h = int(project.get("height", DEFAULT_HEIGHT))
    html = render_html(project, template_name)

    page = await browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    try:
        await page.set_content(html, wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        result = await page.evaluate(FIT_AND_CHECK_JS, {"w": w, "h": h})

        notes = list(result["issues"])
        if result["shrunk"]:
            s = result["shrunk"]
            print(f"  · {project['id']} [{template_name}]: title auto-fit "
                  f"{s['from']:.0f}px -> {s['to']:.0f}px")

        if result["subShrunk"]:
            s = result["subShrunk"]
            print(f"  · {project['id']} [{template_name}]: subtitle auto-fit "
                  f"{s['from']:.0f}px -> {s['to']:.0f}px")

        out = None
        if save:
            out_dir = OUTPUT_DIR / template_name
            out_dir.mkdir(parents=True, exist_ok=True)
            out = out_dir / project["output"]
            await page.screenshot(path=str(out), full_page=False,
                                  clip={"x": 0, "y": 0, "width": w, "height": h})
        return out, notes
    finally:
        await page.close()


async def run(ids: list[str] | None, override: str | None, all_templates: bool,
              save: bool, strict: bool) -> int:
    ps = projects()
    if ids is not None:
        known = {p["id"] for p in ps}
        missing = set(ids) - known
        if missing:
            raise SystemExit("Unknown project(s): " + ", ".join(sorted(missing)))
        ps = [p for p in ps if p["id"] in ids]

    if override and override not in available_templates():
        raise SystemExit(f"Unknown template '{override}'. Available: "
                         f"{', '.join(available_templates())}")

    jobs: list[tuple[dict[str, Any], str]] = []
    for p in ps:
        names = available_templates() if all_templates else [template_of(p, override)]
        for t in names:
            jobs.append((p, t))

    errors = validate_outputs(ps, override, all_templates)
    static_warnings: list[str] = []
    for p, t in jobs:
        e, w = validate(p, t)
        errors += e
        static_warnings += w
    static_warnings = list(dict.fromkeys(static_warnings))

    if errors:
        print("✗ Validation failed:")
        for e in dict.fromkeys(errors):
            print(f"  - {e}")
        return 1
    for w in static_warnings:
        print(f"⚠ {w}")

    layout_problems = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(**browser_launch_kwargs())
        try:
            for proj, t in jobs:
                out, notes = await render_one(browser, proj, t, save)
                if save and out:
                    print(f"✓ {proj['id']} [{t}]: {out.relative_to(ROOT)}")
                elif not notes:
                    print(f"✓ {proj['id']} [{t}]: layout OK")
                for n in notes:
                    layout_problems += 1
                    print(f"⚠ {proj['id']} [{t}]: {n}")
        finally:
            await browser.close()

    if save:
        write_index()

    if layout_problems and strict:
        print(f"\n✗ {layout_problems} layout problem(s) found.")
        return 1
    return 0


# --------------------------------------------------------------------------- #
# Preview pages
# --------------------------------------------------------------------------- #

def write_index() -> Path:
    """output/index.html - every rendered PNG, grouped by template."""
    ps = projects()
    groups = []
    for t in available_templates():
        cards = []
        for p in ps:
            if (OUTPUT_DIR / t / p["output"]).exists():
                cards.append({
                    "src": f"{t}/{p['output']}",
                    "title": f"{p.get('title_prefix', 'FG')} {p['title']}",
                    "subtitle": p.get("subtitle", ""),
                })
        if cards:
            groups.append({"name": t, "cards": cards})
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / "index.html"
    target.write_text(env.get_template("preview.html").render(groups=groups), encoding="utf-8")
    return target


def write_icon_catalog() -> Path:
    names = sorted(p.stem for p in ICONS_DIR.glob("*.svg"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / "icons.html"
    target.write_text(
        env.get_template("icon-catalog.html").render(
            icon_names=names, icon_base="../templates/icons"),
        encoding="utf-8",
    )
    return target


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description="FG Banner Generator v3.3")
    ap.add_argument("command", help="list | check | all | icons | <project-id>")
    ap.add_argument("target", nargs="?", default=None,
                    help="Project id (only used with `check`).")
    ap.add_argument("--template", default=None,
                    help=f"Override the template ({', '.join(available_templates())}).")
    ap.add_argument("--all-templates", action="store_true",
                    help="Render every project in every available template.")
    ap.add_argument("--strict", action="store_true",
                    help="Exit with code 1 on layout warnings (always on for `check`).")
    a = ap.parse_args()

    if a.command == "list":
        for p in projects():
            e, _ = validate(p, template_of(p, a.template))
            flag = "" if not e else "  ✗ " + "; ".join(e)
            print(f"{p['id']:<22} {p['template']:<8} "
                  f"{p.get('title_prefix', 'FG')} {p['title']}{flag}")
        return

    if a.command == "icons":
        print(f"✓ {write_icon_catalog().relative_to(ROOT)}")
        return

    if a.command == "check":
        ids = [a.target] if a.target else None
        code = asyncio.run(run(ids, a.template, a.all_templates, save=False, strict=True))
    elif a.command == "all":
        code = asyncio.run(run(None, a.template, a.all_templates, save=True, strict=a.strict))
    else:
        code = asyncio.run(run([a.command], a.template, a.all_templates,
                               save=True, strict=a.strict))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
