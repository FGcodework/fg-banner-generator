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

## Typography and layout

The text is set in **DejaVu Sans** (Regular + Bold). The font is bundled in `assets/fonts/`
(Latin subset, ~27 kB each, embedded into every banner as a data URI), so the banner looks the
same on every machine and on GitHub Actions, no matter which fonts are installed.

- The earlier hand-made 1200 px banner (checked on FG Watermark) was DejaVu Sans as well. JED shows
  banners at 1200 px width, so the text is sized for that: at 1200 px the description is ~19.5 px, the headings ~25 px, the slogan ~25 px and
  the title ~63 px (the old 1200 px banners had 20 / 25 / 27 / 68 px).
- Title: 84 px, a longer title is shrunk by measurement (min 44 px). Slogan: 34 px, shrunk to one
  line (min 26 px). Feature descriptions: 26 px, if the longest does not fit **all** descriptions of
  the banner shrink together (min 20 px), so they stay equally big.
- The left panel (logo frame) is narrow: 26 % of the width, frame 268 px, inner box 244 px with a
  45 px radius (= 18.5 %, the radius of the logos).
- The Joomla / Free / GPL badges are **off**. Set `"show_badges": true` in `defaults` (or in a
  project) to show them again (`joomla`, `download`, `license` keys).

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
- `watermark`

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
- optional Joomla/version and free/license badges (`show_badges`, off by default)
- one highlighted hero feature (`"hero": true`), aligned on the same icon/text axis as the other rows
- smaller outline feature icons
- automatic title sizing: a long title is shrunk by measurement (down to 44 px) instead of by character count

This keeps the extensions recognizably part of the same FG family while making the banner more suitable for an extension-directory presentation.
