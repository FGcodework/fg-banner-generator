# FG Banner Generator — JED Banner Style

Separate JED-oriented template for the FG Banner Generator (v3.3).

## Files

The original FG master style stays untouched:

- `templates/banner.html`
- `templates/banner.css`

JED uses:

- `templates/jed.html`
- `templates/jed.css`

## Render

`projects.json` sets `"template": "jed"` on every project, so the default run renders JED:

```bash
python render.py all
python render.py email-remover
```

Explicit template / both templates:

```bash
python render.py email-remover --template jed
python render.py all --all-templates
```

Layout check without saving anything (also runs in CI before rendering):

```bash
python render.py check
```

JED output is written to `output/jed/`, the original style to `output/banner/`.
`output/index.html` lists everything that has been rendered, grouped by template.

## Logo

The logo fills the whole square frame (`contain`, so nothing is cropped and non-square
logos keep their ratio). The frame corners are rounded to match the usual ~18 % corner
radius of the FG logos.

- `logo_size` is **not used** by this template any more (the banner template still uses it).
- Fine tuning per project: `logo_scale` (e.g. `0.92` = a bit of air around a glyph without
  margins, `1.04` = compensate a transparent margin in the PNG), `logo_offset_x`, `logo_offset_y`.
- Without a logo the `placeholder_logo` is shown on the dark gradient tile.

## Brand logo (instead of "by <developer>")

The line in the bottom-right corner can show a logo instead of the text `by FGcodework`:

```json
"defaults": {
  "brand_logo": "assets/brand/fgcodework.svg",
  "brand_logo_height": 40
}
```

- `brand_logo` is a path to an SVG or PNG (transparent background, made for the dark banner).
  The logo is right-aligned and sits 22 px above the bottom edge.
- `brand_logo_height` is optional (default 34 px, the width follows the aspect ratio).
- It works per project too: put the same keys into a project to override the default.
- Without `brand_logo` (or if the file is missing - `check` warns) the text `by <developer>` is used.
- `python render.py check` still reports a feature row that would touch the logo.
- Only the `jed` template supports it.

## Projects

- `email-remover`
- `strip-comments`
- `auto-lightbox`
- `fgcustomrightclick`
- `admin-login-customizer`
- `remove-generator`
- `editor-switcher`
- `offline-ip-whitelist`

## Design rationale

The FG logos share a strong visual language:

- deep navy / blue base
- white primary symbol
- coral/orange diagonal or accent element

JED therefore reuses that brand language instead of introducing a new green/teal palette.

The JED layout intentionally differs from the original glossy FG layout:

- more restrained logo frame
- coral FG accent, driven by `palette.panel_glow` in `projects.json`
- category label
- Joomla/version badges
- free/license badges
- one highlighted hero feature (`"hero": true`), aligned on the same icon/text axis as the other rows
- smaller outline feature icons
- automatic title sizing: a long title is shrunk by measurement (down to 44 px) instead of by character count

This keeps the extensions recognizably part of the same FG family while making the banner more suitable for an extension-directory presentation.
