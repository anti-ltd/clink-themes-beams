#!/usr/bin/env python3
"""Generate paired, appearance-only Clink themes from the reviewed palette table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rgba(value: str) -> dict[str, float]:
    value = value.removeprefix('#')
    return {**{channel: round(int(value[index:index + 2], 16) / 255, 8)
               for channel, index in zip('rgb', (0, 2, 4))}, 'a': 1}


def cap(fill: dict, text: dict) -> dict:
    return {'fill': fill, 'text': text, 'activeFill': fill, 'activeText': text}


def appearance(record: dict, dark: bool) -> dict:
    palette = record['dark' if dark else 'light']
    colors = {key: rgba(palette[key]) for key in
              ('background', 'keyFill', 'keyText', 'specialKeyFill', 'specialKeyText')}
    return_fill, return_text = rgba(palette['returnFill']), rgba(palette['returnText'])
    return {
        'id': record['id'], 'name': record['name'], 'source': 'beamsRepository',
        'isDark': dark, **colors, 'accent': return_fill,
        'material': '3d', 'threeDVariant': 'retro', 'retroFinish': 'soft', 'retroDepth': 4,
        'keySurfaceMaterial': 'grain', 'liquidGlass': False,
        'grainDensity': 1, 'grainSize': 0.5, 'grainStrength': 0.025,
        'keyFontDesign': 'default', 'keyFontWeight': 'regular',
        'keyCapShape': 'rect',
        'groupPaint': {
            'letters': {'cornerRadius': 6},
            'numbers': {'cornerRadius': 6},
            'punctuation': {'cornerRadius': 6},
            'modifiers': {'cornerRadius': 6},
            'return': cap(return_fill, return_text),
            'space': cap(colors['keyFill'], colors['keyText']),
            'backspace': {'pressed': return_fill},
        },
    }


def documents() -> dict[Path, str]:
    records = json.loads((ROOT / 'palettes.json').read_text())['themes']
    ids = [record['id'] for record in records]
    assert len(ids) == 22 and len(set(ids)) == 22 and ids[0] == 'beams'
    output = {}
    for record in records:
        light, dark = appearance(record, False), appearance(record, True)
        theme = {**light, 'pairedVariants': [light, dark]}
        output[ROOT / 'Themes' / (record['id'] + '.clinktheme')] = (
            json.dumps(theme, ensure_ascii=False, indent=2) + '\n')
    output[ROOT / 'catalog.json'] = json.dumps({
        'version': 1, 'name': 'Beams',
        'themes': ['Themes/' + theme_id + '.clinktheme' for theme_id in ids],
    }, ensure_ascii=False, indent=2) + '\n'
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if generated files differ')
    args = parser.parse_args()
    stale = []
    for path, content in documents().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        raise SystemExit('Regenerate theme documents: ' + ', '.join(stale))
    print('Beams: 22 paired themes / 44 appearances ' + ('verified' if args.check else 'generated'))


if __name__ == '__main__':
    main()
