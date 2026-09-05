#!/usr/bin/env python3

from __future__ import annotations

import html
from collections import defaultdict
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "resources" / "_nhfp-apps"
OUTPUT_PATH = DATA_DIR / "nhfp-apps-fragment.html"

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


def build_fragment(apps):
    grouped = defaultdict(list)
    for app in apps:
        grouped[app["year"]].append(app)

    html_lines = [
        '<section class="wrapper style4 container">',
        '  <div class="content">',
        '    <section>',
        '      <header>',
        '        <h3>Example NHFP Applications</h3>',
        '      </header>',
    ]

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

            html_lines.append('        <li class="nhfp-app-item">')
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


def main():
    apps = load_apps()
    OUTPUT_PATH.write_text(build_fragment(apps) + "\n", encoding="utf-8")
    print(f"Wrote {len(apps)} NHFP applications to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
