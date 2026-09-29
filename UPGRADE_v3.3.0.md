# Upgrade to FG Banner Generator v3.3.0

## Files to replace

- `render.py`
- `projects.json` (only `defaults.palette` changed: `accent`, `accent_secondary` added)
- `templates/jed.css`, `templates/jed.html`
- `templates/banner.html` (icon include is strict now)
- `templates/preview.html`, `templates/icon-catalog.html`
- `.github/workflows/render.yml`
- `README.md`, `README_JED.md`

Keep `templates/icons/`, `assets/`, `sync_icons.py`, `tabler-icons.json`, `THIRD_PARTY_LICENSES.md`.

## Then run

```bash
python render.py check
python render.py all
git rm output/fg-auto-lightbox.png output/fg-email-remover.png output/fg-strip-comments.png
git add -A
git commit -m "FG Banner Generator v3.3.0"
```

The three PNGs directly in `output/` are leftovers from before templates got their own
sub-directory; nothing writes them any more.

## What changed

Fixes

- The `banner` (master) template lost its accent colour after the JED patch, because
  `accent` / `accent_secondary` were missing from `projects.json`. The "FG" prefix, the
  divider and the icon discs rendered without colour. Restored, and `render.py` now has
  built-in palette fallbacks so a missing key can no longer produce an empty CSS variable.
- `output/index.html` is generated again (it was documented but nothing wrote it) and is
  grouped by template. `python render.py icons` builds `output/icons.html`.
- JED: the highlighted (hero) feature row was inset 14 px further than the other rows.
  All rows now share one icon/text axis. Vertical positions are unchanged.
- JED: the coral accent and the page background now come from the palette
  (`panel_glow`, `background_bottom`). With the default palette the result differs from
  v3.2.1 by at most 8/255 per channel.
- CI: user input no longer goes straight into shell/Python source, the diagnostics look
  into `output/<template>/`, and the push step does `git pull --rebase` first.

New

- `python render.py check [project-id]` – validation + in-browser measurement, saves nothing,
  exit code 1 on problems. Runs in CI before rendering.
- Long titles are auto-fitted by measurement (min 44 px).
- Missing icon, missing required fields and output-file collisions are errors.
  Jinja runs with `StrictUndefined`, so a typo in a template variable is an error, not an empty string.
- One Chromium instance per run instead of one per banner.
- `--all-templates`, and a `FG_CHROMIUM` / `FG_BROWSER_ARGS` environment override.
- Templates are discovered automatically as `templates/<name>.html` + `<name>.css`.
- Workflow input `all_templates`.
