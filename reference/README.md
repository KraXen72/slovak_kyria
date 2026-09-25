# Recovery and reproducibility references

The pinned firmware source baseline is:

- repository: `https://github.com/KraXen72/vial-qmk-legacy.git`
- branch: `vial-avr-legacy`
- commit: `bdbfe655257c63fc86208fbea5435d3585356f2b`

The repository now contains the historical February 2022 firmware reference at
[`known-good/splitkb_kyria_rev1_slovak_kyria.hex`](known-good/splitkb_kyria_rev1_slovak_kyria.hex).
It was copied from the extracted `backup of old vial build` on the local data
drive. Its source timestamp was 2022-02-22 and its SHA-256 is:

```text
ADE9600C4273D8A4DD84631259CD1FC8B27988F8AA608C8EDEF92110AEACB715
```

The January 2022 `latest built kyria keymap.7z` archive contains a different,
older `splitkb_kyria_rev1_slovak_kyria.hex` (67,493 bytes), so it is not used
as the canonical comparison artifact. The corresponding ELF, linker map,
object files, and large `vial-qmk.7z` source archive remain outside this Git
repository in the original data backup.

The retained Vial exports live in [`../vial_saves`](../vial_saves), including
[`v2_36_restore_accents2.vil`](../vial_saves/v2_36_restore_accents2.vil).

`github-baseline/` preserves the older root-level keymap and helper that were
already present in the GitHub repository before the source reorganization. The
active versions are `../firmware/keymap.c` and `../tools/helper.py`.

Older generated keymap images and layout exports are grouped under
[`legacy/`](legacy/); they are retained for comparison only. The current
README image and its reproducible drawer inputs live under
[`../assets`](../assets).

Do not dump, erase, or flash either controller as part of this setup.
