# Create a Clink Beams theme

You are contributing one polished, data-only paired keyboard theme to this repository. First inspect `README.md`, `LICENSE.md`, `palettes.json`, `catalog.json`, `Themes/beams.clinktheme`, one other pair close to the requested colours, `tools/generate.py`, and `tools/build-manifest.py`. Work on the requested colourway only and preserve the other collection entries.

Use the visual direction already supplied. Each colourway needs a complete light and dark palette with readable letter, function, and Return key legends. Keep the Beams collection's shallow 3D Retro style with the Soft finish, fine Grain surface, and consistent keycap shape unless the user explicitly asks to change them.

## Editable source

Edit the requested entry in `palettes.json`. A record has:

- A permanent lowercase `id` beginning with `beams-`, except the first collection entry, whose ID is `beams`.
- A short, clear visible `name`.
- Complete `light` and `dark` objects, each with `background`, `keyFill`, `keyText`, `specialKeyFill`, `specialKeyText`, `returnFill`, and `returnText`.
- Colour values written as six-digit `#RRGGBB` strings.

The generator creates `.clinktheme` documents with numeric RGBA components in the 0–1 range, one shared identity, and exactly two complete `pairedVariants`. The variants must have opposite `isDark` values and cannot contain nested pairs. It also regenerates `catalog.json` in palette-table order. Do not hand-edit generated theme files: regeneration would overwrite those edits.

For an additional colourway, add one record with a unique ID and name. The generator deliberately checks the curated collection count, currently 22; update that count and its status message only when the task intentionally changes the collection size. Preserve the first `beams` entry and all unrelated IDs.

## Scope

Themes change appearance only. Do not add layout settings, key spacing or dimensions, long-press preview visibility, sounds, haptics, input behaviour, photos, artwork assets, or executable code to the theme documents. Keep the existing licence notices and release workflow. Do not change Git configuration as part of a theme request.

The surface field is `keySurfaceMaterial`, independent of the `material` key style. Its supported values are `normal`, `gloss`, `grain`, and `glass`. The current collection uses `grain`, with `material: "3d"`, `threeDVariant: "retro"`, `retroFinish: "soft"`, and `retroDepth: 4`. The authored Grain settings are `grainDensity: 1`, `grainSize: 0.5`, and `grainStrength: 0.025`; preserve them unless the requested appearance calls for different texture. Explicit surface materials take precedence over the legacy `liquidGlass` Boolean; the generator writes `liquidGlass: false` for these Grain themes so older readers do not turn on glass.

## Validation

Run:

```sh
python3 tools/generate.py
python3 tools/generate.py --check
python3 tools/build-manifest.py
python3 tools/build-manifest.py --check
python3 -m unittest discover -s tests
python3 -m json.tool Themes/<your-file>.clinktheme >/dev/null
```

Review the palette, catalog, and generated-document diffs. Check both light and dark appearances in Clink. Source validation alone does not prove the rendered appearance: report whether native visual verification was actually performed.

Keep the README collection listing current. Its preview gallery must use actual Clink renderer captures; do not substitute reference screenshots or generated mockups. Follow the README's preview refresh instructions when fresh native captures are available.

This repository supplies downloadable themes through `manifest.json`. Beams is a default linked, non-removable repository in supported Clink builds; the first release must be published before installation works. Installed themes remain available offline. The manifest contains each complete paired Theme as `preview` and an `asset` with the immutable GitHub release URL, filename, SHA-256, and byte count. Do not add unrelated links, comparison metadata, or executable content.

The workflow publishes on pushes to `main` or manual dispatch. Release tags are derived from the theme documents and catalog, so published assets keep permanent matching URLs. `GITHUB_REPOSITORY` determines the URLs when publishing a fork. Finish by stating which palette and theme document changed, the visual intent, and the checks performed. Do not commit or push unless the user explicitly requests it.
