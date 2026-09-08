#!/usr/bin/env python3

from __future__ import annotations

import csv
import html
import re
from collections import defaultdict
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.cell.rich_text import CellRichText, TextBlock
    from openpyxl.cell.text import InlineFont
    from openpyxl.styles import Alignment, Font, PatternFill
except ImportError:  # pragma: no cover
    Workbook = None
    CellRichText = None
    TextBlock = None
    InlineFont = None
    Alignment = None
    Font = None
    PatternFill = None

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "resources" / "_nhfp-apps"
OUTPUT_DIR = ROOT / "nhfp-apps"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "nhfp-apps-fragment.html"
OUTPUT_CSV_PATH = OUTPUT_DIR / "nhfp-apps.csv"
OUTPUT_XLSX_PATH = OUTPUT_DIR / "nhfp-apps.xlsx"
OUTPUT_TOML_PATH = OUTPUT_DIR / "nhfp-apps.toml"

INSTITUTION_ABBREVIATIONS = {
    "California Institute of Technology": "Caltech",
    "Columbia University": "Columbia",
    "Georgia State University": "Georgia State",
    "Harvard University": "Harvard CfA",
    "Institute for Advanced Study": "IAS",
    "Jet Propulsion Laboratory": "JPL",
    "Lawrence Berkeley National Laboratory": "LBNL",
    "Massachusetts Institute of Technology": "MIT",
    "National Radio Astronomy Observatory": "NRAO",
    "New York University": "NYU",
    "Northwestern University": "Northwestern",
    "Pennsylvania State University": "Penn State",
    "Princeton University": "Princeton",
    "Rutgers University": "Rutgers",
    "Smithsonian Astronomical Observatory": "Harvard CfA",
    "Space Telescope Science Institute": "STScI",
    "Stanford University": "Stanford",
    "The Ohio State University": "Ohio State",
    "University of California, Berkeley": "UC Berkeley",
    "University of California, San Diego": "UCSD",
    "University of California, Santa Barbara": "UCSB",
    "University of California, Santa Cruz": "UC Santa Cruz",
    "University of Chicago": "UChicago",
    "University of Colorado Boulder": "CU Boulder",
    "University of Texas at Austin": "UT Austin",
    "University of Wisconsin–Madison": "University of Wisconsin",
    "Yale University": "Yale",
    "Johns Hopkins University": "Johns Hopkins",
    "Stony Brook University": "Stony Brook",
    "Carnegie Institution for Science's Earth and Planets Laboratory": "Carnegie Science EPL",
}

FLAVOR_COLORS = {
    "Hubble": "#8f1402",
    "Einstein": "#be006c",
    "Sagan": "#cf9306",
    "Chandra": "#5f1b6b",
    "Spitzer": "#fa4224",
    "Michelson": "#b30219",
    "default": "#111111",
}

SCIENCE_CATEGORIES = [
    "Compact Objects and Accretion",
    "Exoplanet Formation and Protoplanetary Disks",
    "Exoplanets and Habitability",
    "Galaxies and the Intergalactic Medium",
    "Gravitational Wave Astrophysics",
    "Physics and Cosmology",
    "Stellar Physics",
    "The Milky Way and Resolved Stellar Populations",
]

def abbreviate_institution(value):
    text = normalize_whitespace(value or "")
    return INSTITUTION_ABBREVIATIONS.get(text, text)


def flavor_color(flavor):
    key = normalize_whitespace(flavor or "")
    return FLAVOR_COLORS.get(key, FLAVOR_COLORS["default"])


def load_apps():
    apps = []
    for path in sorted(DATA_DIR.glob("*.toml")):
        if path.name == "TEMPLATE.toml":
            continue

        with path.open("rb") as fh:
            data = tomllib.load(fh)

        app = {
            "name": str(data.get("name", "")).strip(),
            "year": str(data.get("year", "")).strip(),
            "title": str(data.get("title", "")).strip(),
            "flavor": str(data.get("flavor", "")).strip(),
            "institution_phd": str(data.get("institution_phd", "")).strip(),
            "institution_host": str(data.get("institution_host", "")).strip(),
            "science_category": str(data.get("science_category", "")).strip(),
            "abstract": str(data.get("abstract", "")).strip(),
            "url": str(data.get("url", "")).strip(),
        }

        if app["name"]:
            apps.append(app)

    apps.sort(key=lambda item: (int(item["year"]) if item["year"].isdigit() else -1, item["name"]), reverse=True)
    return apps


def normalize_whitespace(value):
    return " ".join(str(value).split())


def title_or_placeholder(app):
    title = normalize_whitespace(app.get("title") or "")
    if title.lower() in {"nan", "n/a", "na", "none"}:
        return "(unspecified title)"
    return title if title else "(unspecified title)"


SCIENCE_CATEGORY_ALIASES = {
    "compact objects and accretion": "Compact Objects and Accretion",
    "exoplanet formation and protoplanetary disks": "Exoplanet Formation and Protoplanetary Disks",
    "exoplanets and habitability": "Exoplanets and Habitability",
    "galaxies and the intergalactic medium": "Galaxies and the Intergalactic Medium",
    "gravitational wave astrophysics": "Gravitational Wave Astrophysics",
    "physics and cosmology": "Physics and Cosmology",
    "stellar physics": "Stellar Physics",
    "the milky way and resolved stellar populations": "The Milky Way and Resolved Stellar Populations",
}


def category_label(value):
    category = normalize_whitespace(value or "")
    if category.lower() in {"nan", "n/a", "na", "none"}:
        return "Unspecified"
    lowered = category.lower()
    if lowered in SCIENCE_CATEGORY_ALIASES:
        return SCIENCE_CATEGORY_ALIASES[lowered]
    return category if category in SCIENCE_CATEGORIES else "Unspecified"


def hsl_to_hex(hsl_value):
    match = re.match(r"hsl\(\s*(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%\s*\)", hsl_value)
    if not match:
        return "#FFFFFF"
    h, s, l = [float(value) for value in match.groups()]
    s /= 100.0
    l /= 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = l - c / 2
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return "#{:02X}{:02X}{:02X}".format(int(round((r + m) * 255)), int(round((g + m) * 255)), int(round((b + m) * 255)))


def format_toml_value(value):
    if value is None:
        return '""'
    text = str(value).strip()
    if text.lower() in {"nan", "n/a", "na", "none"}:
        return "nan"
    if text == "":
        return '""'
    if text.lower() in {"true", "false"}:
        return text.lower()
    try:
        if text.replace(".", "", 1).replace("-", "", 1).isdigit():
            return text
    except Exception:
        pass
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def build_rich_name_cell(name, flavor):
    if not name:
        name = "(unnamed fellow)"
    flavor_text = normalize_whitespace(flavor or "")
    if flavor_text.lower() in {"nan", "n/a", "na", "none", "unknown"}:
        return name
    return CellRichText([
        TextBlock(font=InlineFont(color="000000"), text=name),
        TextBlock(font=InlineFont(color="000000"), text=" ("),
        TextBlock(font=InlineFont(color=flavor_color(flavor_text).lstrip("#")), text=flavor_text),
        TextBlock(font=InlineFont(color="000000"), text=")"),
    ])


def build_fragment(apps):
    grouped = defaultdict(list)
    for app in apps:
        grouped[app["year"]].append(app)

    category_colors = {
        # key: (button_bg, text_color, item_bg_lighter)
        # Normalize all buttons to the same bright luminance (88%) and item backgrounds to 96%.
        "All": ("hsl(0 0% 88%)", "#1b1b1b", "hsl(0 0% 96%)"),
        # Compact Objects: blue
        "Compact Objects and Accretion": ("hsl(220 76% 88%)", "#1b1b1b", "hsl(220 76% 96%)"),
        # Exoplanet Formation: magenta-ish (inoffensive)
        "Exoplanet Formation and Protoplanetary Disks": ("hsl(320 60% 88%)", "#1b1b1b", "hsl(320 60% 96%)"),
        # Exoplanets & Habitability: pink
        "Exoplanets and Habitability": ("hsl(340 80% 88%)", "#1b1b1b", "hsl(340 80% 96%)"),
        # Galaxies: green
        "Galaxies and the Intergalactic Medium": ("hsl(120 60% 88%)", "#1b1b1b", "hsl(120 60% 96%)"),
        # Gravitational Wave Astrophysics: purple
        "Gravitational Wave Astrophysics": ("hsl(270 60% 88%)", "#1b1b1b", "hsl(270 60% 96%)"),
        # Physics: brown (pale/tan at same luminance)
        "Physics and Cosmology": ("hsl(28 45% 88%)", "#1b1b1b", "hsl(28 45% 96%)"),
        # Stellar Physics: yellow
        "Stellar Physics": ("hsl(55 90% 88%)", "#1b1b1b", "hsl(55 90% 96%)"),
        # Milky Way: teal
        "The Milky Way and Resolved Stellar Populations": ("hsl(190 60% 88%)", "#1b1b1b", "hsl(190 60% 96%)"),
    }

    html_lines = [
        '<section class="wrapper style4 container">',
        '  <div class="content">',
        '    <section>',
        '      <header>',
        '        <h3>Example NHFP Applications</h3>',
        '      </header>',
        '      <div class="nhfp-category-filter-bar">',
        '        <button class="nhfp-category-button active" data-nhfp-category="all" type="button" style="background-color:#dfe4e7; color:#1b1b1b; --nhfp-button-bg:#dfe4e7; --nhfp-button-fg:#1b1b1b;">All</button>',
    ]

    for category in SCIENCE_CATEGORIES:
        label = html.escape(category)
        color, text_color, _ = category_colors.get(category, ("hsl(0 0% 92%)", "#1b1b1b", "#f3f3f3"))
        html_lines.append(f'        <button class="nhfp-category-button" data-nhfp-category="{html.escape(category, quote=True)}" type="button" style="--nhfp-button-bg:{color}; --nhfp-button-fg:{text_color};">{label}</button>')

    html_lines.append('      </div>')

    for year in sorted(grouped.keys(), key=lambda value: int(value) if value.isdigit() else -1, reverse=True):
        html_lines.append(f'      <h4 class="nhfp-year-heading">{html.escape(year)}</h4>')
        html_lines.append('      <ul class="nhfp-apps-list">')

        for app in grouped[year]:
            title = title_or_placeholder(app)
            app_link = app.get("url")
            if title.lower() == "(unspecified title)":
                title_html = '<em>(unspecified title)</em>'
            else:
                title_html = html.escape(title)
            if app_link:
                title_html = f'<a href="{html.escape(app_link, quote=True)}" target="_blank" rel="noopener noreferrer">{title_html}</a>'

            name = html.escape(normalize_whitespace(app.get("name") or "(unnamed fellow)"))
            flavor_raw = normalize_whitespace(app.get("flavor") or "unknown")
            flavor = html.escape(flavor_raw)
            flavor_style = f'color: {flavor_color(flavor_raw)};'
            host = html.escape(abbreviate_institution(app.get("institution_host") or "(unspecified host)"))
            abstract = normalize_whitespace(app.get("abstract") or "")
            if abstract.lower() in {"nan", "n/a", "na", "none"}:
                abstract = ""
            category = category_label(app.get("science_category"))
            item_bg = category_colors.get(category, ("hsl(0 0% 96%)", "#1b1b1b", "hsl(0 0% 97%)"))[2]

            html_lines.append('        <li class="nhfp-app-item" data-category="' + html.escape(category, quote=True) + '" style="--nhfp-item-bg:' + item_bg + ';">')
            html_lines.append(f'          <div class="nhfp-app-title">{title_html}</div>')
            html_lines.append(f'          <div class="nhfp-app-fellow">{name} (<span style="{flavor_style}">{flavor}</span> @ {host})</div>')
            if abstract:
                html_lines.append('          <details class="nhfp-app-details">')
                html_lines.append('            <summary>Abstract</summary>')
                html_lines.append(f'            <div class="nhfp-app-abstract"><em>{html.escape(abstract)}</em></div>')
                html_lines.append('          </details>')
            html_lines.append('        </li>')

        html_lines.append('      </ul>')

    html_lines.extend([
        '    </section>',
        '  </div>',
        '</section>',
    ])
    return "\n".join(html_lines)


def write_csv(apps):
    rows = []
    for app in apps:
        name = normalize_whitespace(app.get("name") or "")
        year = normalize_whitespace(app.get("year") or "")
        category = category_label(app.get("science_category"))
        title = title_or_placeholder(app)
        link = normalize_whitespace(app.get("url") or "")
        rows.append([name, year, category, title, link])

    with OUTPUT_CSV_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["fellow", "year", "category", "title", "link"])
        writer.writerows(rows)


def write_toml(apps):
    lines = []
    for app in apps:
        lines.append("[[apps]]")
        lines.append(f'name = {format_toml_value(normalize_whitespace(app.get("name") or ""))}')
        lines.append(f'year = {format_toml_value(normalize_whitespace(app.get("year") or ""))}')
        lines.append(f'category = {format_toml_value(category_label(app.get("science_category")))}')
        lines.append(f'title = {format_toml_value(title_or_placeholder(app))}')
        lines.append(f'flavor = {format_toml_value(normalize_whitespace(app.get("flavor") or ""))}')
        lines.append(f'institution_phd = {format_toml_value(normalize_whitespace(app.get("institution_phd") or ""))}')
        lines.append(f'institution_host = {format_toml_value(normalize_whitespace(app.get("institution_host") or ""))}')
        lines.append(f'abstract = {format_toml_value(normalize_whitespace(app.get("abstract") or ""))}')
        lines.append(f'url = {format_toml_value(normalize_whitespace(app.get("url") or ""))}')
        lines.append("")
    OUTPUT_TOML_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_xlsx(apps):
    if Workbook is None or CellRichText is None or TextBlock is None or Alignment is None or Font is None or PatternFill is None:
        raise RuntimeError("openpyxl is required for Excel export.")

    category_colors = {
        "All": ("hsl(0 0% 88%)", "#1b1b1b", "hsl(0 0% 96%)"),
        "Compact Objects and Accretion": ("hsl(220 76% 88%)", "#1b1b1b", "hsl(220 76% 96%)"),
        "Exoplanet Formation and Protoplanetary Disks": ("hsl(320 60% 88%)", "#1b1b1b", "hsl(320 60% 96%)"),
        "Exoplanets and Habitability": ("hsl(340 80% 88%)", "#1b1b1b", "hsl(340 80% 96%)"),
        "Galaxies and the Intergalactic Medium": ("hsl(120 60% 88%)", "#1b1b1b", "hsl(120 60% 96%)"),
        "Gravitational Wave Astrophysics": ("hsl(270 60% 88%)", "#1b1b1b", "hsl(270 60% 96%)"),
        "Physics and Cosmology": ("hsl(28 45% 88%)", "#1b1b1b", "hsl(28 45% 96%)"),
        "Stellar Physics": ("hsl(55 90% 88%)", "#1b1b1b", "hsl(55 90% 96%)"),
        "The Milky Way and Resolved Stellar Populations": ("hsl(190 60% 88%)", "#1b1b1b", "hsl(190 60% 96%)"),
    }

    wb = Workbook()
    ws = wb.active
    ws.title = "NHFP Applications"
    ws.freeze_panes = "A2"
    headers = ["fellow", "year", "category", "application"]
    ws.append(headers)

    for header_cell in ws[1]:
        header_cell.font = Font(bold=True, color="000000")
        header_cell.fill = PatternFill("solid", fgColor="D9D9D9")
        header_cell.alignment = Alignment(horizontal="center")

    for row_idx, app in enumerate(apps, start=2):
        name = normalize_whitespace(app.get("name") or "")
        year = normalize_whitespace(app.get("year") or "")
        category = category_label(app.get("science_category"))
        title = title_or_placeholder(app)
        app_link = normalize_whitespace(app.get("url") or "")
        flavor = normalize_whitespace(app.get("flavor") or "")
        fill_color = hsl_to_hex(category_colors.get(category, ("hsl(0 0% 96%)", "#1b1b1b", "hsl(0 0% 96%)"))[2])
        fill = PatternFill("solid", fgColor=fill_color.lstrip("#"))
        for col_idx in range(1, 5):
            ws.cell(row=row_idx, column=col_idx).fill = fill
            ws.cell(row=row_idx, column=col_idx).alignment = Alignment(vertical="top")

        ws.cell(row=row_idx, column=1, value=build_rich_name_cell(name, flavor))
        ws.cell(row=row_idx, column=2, value=year)
        ws.cell(row=row_idx, column=3, value=category)
        title_cell = ws.cell(row=row_idx, column=4, value=title)
        title_cell.fill = fill
        title_cell.font = Font(italic=True)
        if app_link:
            title_cell.hyperlink = app_link
            title_cell.style = "Hyperlink"
            title_cell.font = Font(italic=True, underline="single", color="0563C1")
            title_cell.fill = fill

    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 12), 80)

    ws.sheet_view.showGridLines = False
    wb.save(OUTPUT_XLSX_PATH)


def main():
    apps = load_apps()
    OUTPUT_PATH.write_text(build_fragment(apps) + "\n", encoding="utf-8")
    write_csv(apps)
    write_toml(apps)
    write_xlsx(apps)
    print(f"Wrote {len(apps)} NHFP applications to {OUTPUT_PATH}")
    print(f"Wrote CSV to {OUTPUT_CSV_PATH}")
    print(f"Wrote TOML to {OUTPUT_TOML_PATH}")
    print(f"Wrote XLSX to {OUTPUT_XLSX_PATH}")


if __name__ == "__main__":
    main()
