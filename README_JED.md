# FG Banner Generator — JED Banner Style v1

This patch adds a separate JED-oriented template to the existing FG Banner Generator v3.2.1.

## Important

The existing `templates/banner.html` and `templates/banner.css` remain the original FG master style.

JED uses:

- `templates/jed.html`
- `templates/jed.css`

The three existing projects are configured with their real repository logo paths:

- `assets/logos/email-remover.png`
- `assets/logos/strip-comments.png`
- `assets/logos/auto-lightbox.png`

## Render

Existing FG style:

```bash
python render.py email-remover
```

JED style:

```bash
python render.py email-remover --template jed
python render.py strip-comments --template jed
python render.py auto-lightbox --template jed
```

All three:

```bash
python render.py all --template jed
```

JED output is written to:

```text
output/jed/
```

## Design rationale

The three real FG logos already share a strong visual language:

- deep navy / blue base
- white primary symbol
- coral/orange diagonal or accent element

JED v1 therefore uses that existing brand language instead of introducing a new green/teal palette.

The JED layout intentionally differs from the original glossy FG layout:

- more restrained logo frame
- orange/coral FG accent
- category label
- Joomla/version badges
- free/license badges
- one highlighted hero feature
- smaller outline feature icons
- automatic title sizing for longer extension names

This keeps the three extensions recognizably part of the same FG family while making the banner more suitable for an extension-directory presentation.
