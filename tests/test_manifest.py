import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for folder in ['Themes', 'tools']:
            shutil.copytree(source / folder, self.root / folder,
                            ignore=shutil.ignore_patterns('._*', '__pycache__'))
        for name in ['palettes.json', 'catalog.json']:
            shutil.copyfile(source / name, self.root / name)

    def run_tool(self, name, *args, repository='example/themes'):
        return subprocess.run([sys.executable, str(self.root / 'tools' / name), *args],
                              check=True, capture_output=True,
                              env={**os.environ, 'GITHUB_REPOSITORY': repository})

    def build(self, repository='example/themes'):
        self.run_tool('build-manifest.py', repository=repository)
        return json.loads((self.root / 'manifest.json').read_text())

    def test_all_paired_themes_match_release_assets_and_previews(self):
        manifest = self.build()
        catalog = json.loads((self.root / 'catalog.json').read_text())
        self.assertEqual(len(manifest['themes']), 22)
        self.assertEqual([entry['id'] for entry in manifest['themes']],
                         [Path(path).stem for path in catalog['themes']])
        self.assertEqual(manifest['themes'][0]['id'], 'beams')
        for entry in manifest['themes']:
            self.assertEqual(set(entry), {'id', 'name', 'version', 'preview', 'asset'})
            raw = (self.root / 'Themes' / entry['asset']['path']).read_bytes()
            theme = json.loads(raw)
            self.assertEqual(theme, entry['preview'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['asset']['sha256'])
            self.assertEqual(len(raw), entry['asset']['byteCount'])
            self.assertLessEqual(len(raw), 128_000)
            self.assertEqual(entry['version'], manifest['version'])
            self.assertEqual(entry['asset']['url'],
                             f'https://github.com/example/themes/releases/download/{manifest["version"]}/{entry["id"]}.clinktheme')
            variants = theme['pairedVariants']
            self.assertEqual([variant['isDark'] for variant in variants], [False, True])
            for variant in variants:
                self.assertEqual(variant['id'], entry['id'])
                self.assertNotIn('pairedVariants', variant)
                self.assertEqual(variant['retroFinish'], 'soft')
                self.assertEqual(variant['keySurfaceMaterial'], 'grain')

    def test_repeat_builds_ignore_appledouble(self):
        first = self.build()
        (self.root / 'Themes' / '._junk.clinktheme').write_bytes(b'junk')
        self.assertEqual(first, self.build())
        self.run_tool('build-manifest.py', '--check')

    def test_palette_change_gets_a_new_immutable_release(self):
        first = self.build()
        path = self.root / 'palettes.json'
        palettes = json.loads(path.read_text())
        palettes['themes'][0]['light']['background'] = '#123456'
        path.write_text(json.dumps(palettes))
        with self.assertRaises(subprocess.CalledProcessError):
            self.build()
        self.run_tool('generate.py')
        second = self.build()
        self.assertNotEqual(first['version'], second['version'])
        self.assertNotEqual(first['themes'][0]['asset']['sha256'], second['themes'][0]['asset']['sha256'])

    def test_stale_or_unlisted_theme_cannot_be_published(self):
        path = self.root / 'Themes' / 'beams.clinktheme'
        original = path.read_bytes()
        path.write_bytes(original + b' ')
        with self.assertRaises(subprocess.CalledProcessError):
            self.build()
        path.write_bytes(original)
        (self.root / 'Themes' / 'unlisted.clinktheme').write_bytes(original)
        with self.assertRaises(subprocess.CalledProcessError):
            self.build()

    def test_missing_theme_cannot_be_published(self):
        (self.root / 'Themes' / 'beams.clinktheme').unlink()
        with self.assertRaises(subprocess.CalledProcessError):
            self.build()

    def test_check_rejects_stale_manifest(self):
        self.build()
        (self.root / 'manifest.json').write_text('{}\n')
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_tool('build-manifest.py', '--check')

    def test_fork_urls_follow_publishing_repository(self):
        manifest = self.build(repository='another-owner/beams-fork')
        self.assertTrue(all(entry['asset']['url'].startswith('https://github.com/another-owner/beams-fork/')
                            for entry in manifest['themes']))
        with self.assertRaises(subprocess.CalledProcessError):
            self.build(repository='invalid/repo/extra')


if __name__ == '__main__':
    unittest.main()
