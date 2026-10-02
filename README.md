# FG Banner Generator v3.3

Finálna HTML/CSS + Jinja2 + Playwright verzia generátora jednotných FG bannerov v pomere **16:7**.

## Cieľ

Jedným skriptom generovať bannery, ktoré patria do jednej produktovej rodiny:

- tmavomodré technologické pozadie
- veľký glossy panel s logom naľavo
- výrazný headline na pravej strane
- slogan, divider line a 3–4 feature rows
- jednotná typografia a ikonografia

## Použitie

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Zoznam projektov:

```bash
python render.py list
```

Jeden banner:

```bash
python render.py email-remover
```

Všetky bannery:

```bash
python render.py all
```

Kontrola bez ukladania (validácia + meranie layoutu, pozri nižšie):

```bash
python render.py check
python render.py check email-remover
```

Iná šablóna, alebo všetky šablóny naraz:

```bash
python render.py email-remover --template banner
python render.py all --all-templates
```

Katalóg ikon (`output/icons.html`):

```bash
python render.py icons
```

PNG bannery vznikajú v `output/<šablóna>/` (napr. `output/jed/`) a náhľadová stránka `output/index.html` zoskupuje všetky vyrenderované bannery podľa šablóny.

## Obsah repozitára

```text
fg-banner-generator/
├── render.py
├── projects.json
├── requirements.txt
├── sync_icons.py
├── tabler-icons.json
├── templates/
│   ├── banner.html / banner.css     # pôvodný FG master štýl
│   ├── jed.html / jed.css           # štýl pre adresár rozšírení (JED)
│   ├── preview.html                 # -> output/index.html
│   ├── icon-catalog.html            # -> output/icons.html
│   └── icons/*.svg
├── assets/logos/
├── output/
│   ├── jed/  (banner/)              # PNG podľa šablóny
│   ├── index.html
│   └── icons.html
└── .github/workflows/render.yml
```

## Testovacie projekty

Aktuálne sú pripravené tieto konfigurácie:

- `email-remover`
- `strip-comments`
- `auto-lightbox`
- `fgcustomrightclick`
- `admin-login-customizer`
- `remove-generator`
- `editor-switcher`
- `offline-ip-whitelist`
- `watermark`
- `responsive-tables`

## Šablóny

Šablóna je dvojica `templates/<názov>.html` + `templates/<názov>.css`. Zoznam šablón sa zisťuje automaticky, takže novú šablónu stačí pridať ako takúto dvojicu, bez zásahu do `render.py`.

- `banner` – pôvodný FG master štýl
- `jed` – štýl pre adresár rozšírení (kategória, jeden zvýraznený feature; písmo DejaVu Sans je súčasťou repa v `assets/fonts/`; badge Joomla/Free/GPL sú vypnuté, zapnú sa cez `show_badges`)

Šablóna sa vyberá v `projects.json` cez `"template"` (štandardne `banner`), alebo jednorazovo cez `--template`. Všetky projekty v `projects.json` majú aktuálne `"template": "jed"`, takže `python render.py all` renderuje JED. Master štýl vyrenderuješ cez `--template banner` alebo `--all-templates`.

Poznámka: rozmer banneru je pevne daný CSS (1600×700). `width`/`height` v `projects.json` menia len výrez screenshotu. `check` na to upozorní.

## Kontrola layoutu (`check`)

Pred renderom (a v CI pred commitom) sa robí:

**Statická validácia** – chyba zastaví beh:
- chýbajúce `id`/`title`/`features`, chýbajúce polia vo feature,
- ikona, ktorá neexistuje v `templates/icons/`,
- neexistujúca šablóna,
- dva projekty zapisujúce rovnaký výstupný súbor.

**Meranie v prehliadači** (po načítaní fontov):
- dlhý titulok sa automaticky zmenší (najviac na 44 px),
- text orezaný horizontálne (`white-space: nowrap`), text príliš blízko okraja,
- slogan, ktorý sa nezmestí na jeden riadok (najprv sa automaticky zmenší, najviac na 26 px),
- popisy features, ktoré sa nezmestia (zmenšia sa všetky spoločne, najviac na 20 px),
- prekryv posledného feature s riadkom „by <developer>“.

`check` (a `--strict`) pri takomto probléme skončí s kódom 1. Bez `--strict` sa banner aj tak vyrenderuje a problém sa vypíše ako `⚠`.

Chýbajúce logo nie je chyba, použije sa `placeholder_logo` a vypíše sa upozornenie.

## Farebná paleta

Farby sa berú z `defaults.palette` v `projects.json`, prípadne z `palette` konkrétneho projektu. Ak kľúč chýba, použije sa vstavaná hodnota z `render.py`, takže CSS premenná nikdy nezostane prázdna.

| kľúč | používa |
| --- | --- |
| `background_top`, `background_bottom` | pozadie (obe šablóny) |
| `text_primary`, `text_secondary` | texty |
| `panel_glow` | koralový akcent šablóny **jed** (prefix „FG“, divider, ikony, badge) |
| `accent`, `accent_secondary` | akcent šablóny **banner** (prefix „FG“, divider, kruhy ikon) |

Príklad – modrý akcent len pre jeden projekt:

```json
"palette": { "panel_glow": "#3D8BFF" }
```

(`panel_fill` a `panel_border` sa momentálne v žiadnej šablóne nepoužívajú.)

## Feature riadky

```json
{
  "icon": "shield",
  "heading": "Remove or replace",
  "description": "strip mailto: links & plain-text addresses site-wide",
  "hero": true
}
```

`hero: true` zvýrazní riadok v šablóne `jed` (má byť najviac jeden).

## Pridanie nového pluginu

1. vlož logo do `assets/logos/`
2. pridaj nový objekt do `projects.json`
3. spusti `python render.py <project-id>`

Vo väčšine prípadov nie je potrebné meniť Python ani CSS.

## Poznámka k logám

Ak reálne logo ešte nemáš pripravené, generátor použije `placeholder_logo`. To umožňuje rýchlo testovať layout aj bez finálnych assetov.

## FG Banner Style v1

Táto verzia je považovaná za základný master štýl pre ďalšie FG bannery. Pri ďalších pluginoch by sa mali meniť už len:

- logo
- názov
- slogan
- typ rozšírenia
- zoznam hlavných vlastností


## Logo tuning per project

V3.1 podporuje tieto parametre v `projects.json`:

```json
"logo_mode": "contain",
"logo_size": "90%",
"logo_scale": 1.0,
"logo_offset_x": 0,
"logo_offset_y": 0
```

Význam:

- `logo_mode` – `contain` alebo `full`
- `logo_size` – základná šírka/výška loga v paneli, napr. `90%` alebo `100%`
- `logo_scale` – jemné optické zväčšenie/zmenšenie, napr. `0.95`, `1`, `1.08`
- `logo_offset_x` – horizontálny posun v px
- `logo_offset_y` – vertikálny posun v px

Príklady:

```json
"logo_mode": "contain",
"logo_size": "90%",
"logo_scale": 1.0
```

```json
"logo_mode": "full",
"logo_size": "100%",
"logo_scale": 1.05,
"logo_offset_x": 0,
"logo_offset_y": 0
```


## Tabler Icons – V3.2

V3.2 štandardizuje feature ikonky na **Tabler Icons / Outline**. Tabler používa
24×24 mriežku a 2px stroke, takže ikony sú vizuálne konzistentné naprieč bannermi.

Kurátorovaná sada je definovaná v:

```text
tabler-icons.json
```

Aktuálne obsahuje viac než 30 praktických ikon, napr.:

```text
shield
shield-check
image
photo
code
puzzle
bolt
broom
link
check
database
world
lock
settings
language
eye
file
files
mail
at
user
users
search
filter
download
upload
refresh
trash
replace
device-desktop
browser
server
```

### Synchronizácia ikon

Pred prvým lokálnym renderom alebo po zmene `tabler-icons.json`:

```bash
python sync_icons.py
```

Alebo iba konkrétne ikonky:

```bash
python sync_icons.py database server lock
```

V CI sa ikony nesťahujú (od V3.2.1 sú commitnuté v repozitári), `sync_icons.py` spúšťaj len lokálne.

### Použitie v projects.json

```json
{
  "icon": "database",
  "heading": "Database access",
  "description": "..."
}
```

Generátor následne vloží:

```text
templates/icons/database.svg
```

### Vlastná ikona

Stále môžeš pridať aj vlastné SVG priamo do `templates/icons/`.
Ak napríklad vytvoríš:

```text
templates/icons/my-special-icon.svg
```

v `projects.json` použiješ:

```json
"icon": "my-special-icon"
```

Odporúčané je držať vlastné ikony v rovnakom štýle: `viewBox="0 0 24 24"`,
outline, `currentColor`, približne 2px stroke.

Licenčné informácie pre Tabler sú v `THIRD_PARTY_LICENSES.md`.


## V3.2.1 – lokálne uložené Tabler ikony

Od V3.2.1 sa Tabler SVG ikony pri bežnom renderovaní **nesťahujú z internetu**.

Ikony sú uložené priamo v:

```text
templates/icons/
```

a sú súčasťou Git repozitára. Preto je render:

- rýchlejší,
- deterministický,
- nezávislý od dostupnosti Tabler/GitHub serverov,
- vhodný aj pre offline lokálne renderovanie.

`sync_icons.py` zostáva v repozitári iba ako servisný nástroj. Použi ho len vtedy,
keď chceš aktualizovať existujúce Tabler ikony alebo pridať nové podľa
`tabler-icons.json`.

Príklad:

```bash
python sync_icons.py database server lock
```

Po synchronizácii nové/aktualizované SVG normálne commitni do Git repozitára.
GitHub Actions ich potom pri renderi už iba použije a nič nesťahuje.
