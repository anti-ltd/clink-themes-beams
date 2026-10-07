#!/usr/bin/env python3
"""Build the immutable release manifest for the paired Beams theme catalog."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

from generate import ROOT, documents


def build(repository: str) -> str:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', repository):
        raise SystemExit('GITHUB_REPOSITORY must be owner/repository')

    expected = documents()
    for path, content in expected.items():
        if not path.is_file() or path.read_text() != content:
            raise SystemExit(f'Regenerate theme documents: {path.relative_to(ROOT)}')
    paths = [path for path in expected if path.suffix == '.clinktheme']
    actual = {path for path in (ROOT / 'Themes').glob('*.clinktheme') if not path.name.startswith('.')}
    if actual != set(paths):
        raise SystemExit('Themes/ must contain exactly the catalogued theme documents')

    # Include ordering metadata so every manifest byte is tied to its release.
    release_files = [ROOT / 'catalog.json', *paths]
    identity = [(str(path.relative_to(ROOT)), hashlib.sha256(path.read_bytes()).hexdigest())
                for path in release_files]
    version = 'themes-' + hashlib.sha256(json.dumps(identity, separators=(',', ':')).encode()).hexdigest()
    base = f'https://github.com/{repository}/releases/download/{version}'
    entries = []
    for path in paths:
        raw = path.read_bytes()
        theme = json.loads(raw)
        if not 0 < len(raw) <= 128_000:
            raise SystemExit(f'{path.name}: theme exceeds the app size limit')
        if theme['id'] != path.stem:
            raise SystemExit(f'{path.name}: filename must match the theme ID')
        entries.append({
            'id': theme['id'], 'name': theme['name'], 'version': version,
            'preview': theme,
            'asset': {'path': path.name, 'url': f'{base}/{path.name}',
                      'sha256': hashlib.sha256(raw).hexdigest(), 'byteCount': len(raw)},
        })
    return json.dumps({'version': version, 'themes': entries}, ensure_ascii=False, indent=2) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if the release manifest is stale')
    args = parser.parse_args()
    content = build(os.environ.get('GITHUB_REPOSITORY', 'anti-ltd/clink-themes-beams'))
    path = ROOT / 'manifest.json'
    if args.check:
        if not path.is_file() or path.read_text() != content:
            raise SystemExit('Regenerate the release manifest: python3 tools/build-manifest.py')
    else:
        path.write_text(content)
    print(f'Beams: 22 paired release themes {"verified" if args.check else "generated"}')


if __name__ == '__main__':
    main()
