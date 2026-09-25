# Recovery and reproducibility references

The pinned firmware source baseline is:

- repository: `https://github.com/KraXen72/vial-qmk-legacy.git`
- branch: `vial-avr-legacy`
- commit: `bdbfe655257c63fc86208fbea5435d3585356f2b`

This checkout does not currently contain the historical February 2022 HEX,
ELF, linker map, object archive, or `vial-qmk.7z` source archive. Until those
files are catalogued and copied into a controlled location, `infra/scripts/verify.sh`
checks repeated clean builds but skips comparison with the historical HEX.

The retained Vial exports live in [`../vial_saves`](../vial_saves), including
[`v2_36_restore_accents2.vil`](../vial_saves/v2_36_restore_accents2.vil).

`github-baseline/` preserves the older root-level keymap and helper that were
already present in the GitHub repository before the source reorganization. The
active versions are `../firmware/keymap.c` and `../tools/helper.py`.

Older generated keymap images and layout exports are grouped under
[`legacy/`](legacy/); they are retained for comparison only. The current
README image and its reproducible drawer inputs live under
[`../assets`](../assets).

Do not dump, erase, or flash either controller as part of this setup. Add a
known-good HEX under `reference/known-good/` only after its provenance and
hash have been recorded here.
