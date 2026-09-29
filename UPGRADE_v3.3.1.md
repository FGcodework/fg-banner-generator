# Upgrade to FG Banner Generator v3.3.1

Adds the `admin-login-customizer` project (FG Admin Login Customizer), JED style.

Files:

- `projects.json` (new project appended at the end)
- `assets/logos/admin-login-customizer.png` (logo reconstructed from the old banner - replace it with the original if you have it)
- `output/jed/fg-admin-login-customizer.png`, `output/index.html`
- `README.md`, `README_JED.md` (project list)

```bash
python render.py check admin-login-customizer
python render.py admin-login-customizer
```
