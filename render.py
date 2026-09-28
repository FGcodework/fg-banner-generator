#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import mimetypes
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent
PROJECTS_FILE = ROOT / "projects.json"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def load_data() -> dict[str, Any]:
    return json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))


def merged_project(data, project):
    defaults = dict(data.get("defaults", {}))
    theme_name = project.get("theme", defaults.get("theme", "orange"))
    theme = data.get("themes", {}).get(theme_name, {})

    cfg = {}
    cfg.update(defaults)
    cfg.update(project)

    palette = {}
    palette.update(defaults.get("palette", {}))
    palette.update(theme.get("palette", {}))
    palette.update(project.get("palette", {}))
    cfg["palette"] = palette

    cfg.setdefault("template", "banner")
    cfg.setdefault("joomla", [])
    cfg.setdefault("badges", [])
    cfg.setdefault("category", {})
    cfg.setdefault("license", "")
    cfg.setdefault("download", "")
    cfg.setdefault("developer", "")

    return cfg


def projects():
    data = load_data()
    return [merged_project(data, p) for p in data.get("projects", [])]


def asset_data_uri(relative_path):
    if not relative_path:
        return None

    p = (ROOT / relative_path).resolve()
    if not p.exists():
        return None

    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def render_html(project, template_override=None):
    template_name = template_override or project.get("template", "banner")

    if template_name == "jed":
        html_template = "jed.html"
        css_file = "jed.css"
    else:
        html_template = "banner.html"
        css_file = "banner.css"

    t = env.get_template(html_template)

    ctx = dict(project)
    ctx["logo_uri"] = asset_data_uri(project.get("logo"))
    ctx["css_text"] = (TEMPLATES_DIR / css_file).read_text(encoding="utf-8")
    ctx["template_name"] = template_name

    return t.render(**ctx)


async def render_png(project, template_override=None):
    template_name = template_override or project.get("template", "banner")

    out_dir = OUTPUT_DIR / template_name
    out_dir.mkdir(parents=True, exist_ok=True)

    w = int(project.get("width", 1600))
    h = int(project.get("height", 700))
    output_name = project.get("output", f"{project['id']}.png")
    out = out_dir / output_name

    html = render_html(project, template_override)

    async with async_playwright() as p:
        chromium = (
            shutil.which("chromium")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome")
        )
        launch_args = {"executable_path": chromium} if chromium else {}

        browser = await p.chromium.launch(**launch_args)
        page = await browser.new_page(
            viewport={"width": w, "height": h},
            device_scale_factor=1,
        )
        await page.set_content(html, wait_until="networkidle")
        await page.screenshot(
            path=str(out),
            full_page=False,
            clip={"x": 0, "y": 0, "width": w, "height": h},
        )
        await browser.close()

    return out


async def render_selected(ids=None, template_override=None):
    ps = projects()

    if ids is not None:
        known = {p["id"] for p in ps}
        missing = set(ids) - known
        if missing:
            raise SystemExit(
                "Unknown project(s): " + ", ".join(sorted(missing))
            )
        ps = [p for p in ps if p["id"] in ids]

    for p in ps:
        out = await render_png(p, template_override)
        print(f"✓ {p['id']}: {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description="FG Banner Generator v3")
    ap.add_argument("command", help="list | all | <project-id>")
    ap.add_argument(
        "--template",
        choices=["banner", "jed"],
        default=None,
        help="Override the template. Existing default is banner; JED is jed.",
    )
    a = ap.parse_args()

    if a.command == "list":
        for p in projects():
            print(f"{p['id']:<22} {p.get('title_prefix', 'FG')} {p['title']}")
    elif a.command == "all":
        asyncio.run(render_selected(template_override=a.template))
    else:
        asyncio.run(render_selected([a.command], template_override=a.template))


if __name__ == "__main__":
    main()
