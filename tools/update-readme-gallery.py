#!/usr/bin/env python3
"""Copy native Beams keyboard captures and refresh the paired README gallery.

Pass the directory printed by captureBeamsPairedTheme's KEY_MATERIAL_QA logs.
Images must be the unmodified Clink renderer captures, not reference screenshots.
"""

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", type=Path)
    args = parser.parse_args()
    catalog = json.loads((ROOT / "catalog.json").read_text())
    sources = [(relative, json.loads((ROOT / relative).read_text())) for relative in catalog["themes"]]
    captures = {}
    for _, theme in sources:
        for appearance in ("light", "dark"):
            key = f'{theme["id"]}-{appearance}'
            path = args.captures / f"clink-{key}.png"
            if not path.is_file() or not path.read_bytes().startswith(PNG_HEADER):
                raise SystemExit(f"Missing native PNG capture: {path}")
            captures[key] = path

    preview_dir = ROOT / "README-assets" / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    checksums = {}
    for relative, theme in sources:
        for appearance in ("light", "dark"):
            key = f'{theme["id"]}-{appearance}'
            destination = preview_dir / f"{key}.png"
            shutil.copyfile(captures[key], destination)
            checksums[key] = {
                "themeSHA256": digest(ROOT / relative),
                "previewSHA256": digest(destination),
            }
    (ROOT / "README-assets" / "preview-manifest.json").write_text(json.dumps(checksums, indent=2) + "\n")

    def cell(relative, theme, appearance):
        name = html.escape(theme["name"])
        label = f"{name} {appearance.title()}"
        image = f'README-assets/previews/{theme["id"]}-{appearance}.png'
        return (f'<a href="{relative}"><strong>{label}</strong></a><br>'
                f'<a href="{image}"><img src="{image}" width="400" alt="{label} keyboard preview"></a>')

    lines = ["<!-- theme-gallery:start -->", "## Included themes", "",
             f"{len(sources)} paired keyboard themes. Select a name to open its theme file, or a preview to see it at full size. Each file includes both appearances.",
             "", "| Light | Dark |", "| --- | --- |"]
    for relative, theme in sources:
        lines.append(f'| {cell(relative, theme, "light")} | {cell(relative, theme, "dark")} |')
    lines += ["", "The complete collection is under [`Themes/`](Themes). [`catalog.json`](catalog.json) lists the themes in their display order.",
              "<!-- theme-gallery:end -->"]
    readme = ROOT / "README.md"
    updated, count = re.subn(r"<!-- theme-gallery:start -->.*?<!-- theme-gallery:end -->",
                            "\n".join(lines), readme.read_text(), count=1, flags=re.S)
    if count != 1:
        raise SystemExit("README is missing its theme-gallery markers")
    readme.write_text(updated)
    print(f"Beams: {len(captures)} native previews and README entries updated")


if __name__ == "__main__":
    main()
