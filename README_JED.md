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

## Projects

- `email-remover`
- `strip-comments`
- `auto-lightbox`
- `fgcustomrightclick`
- `admin-login-customizer`

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
