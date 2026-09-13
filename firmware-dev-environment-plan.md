# Kyria legacy firmware development and recovery plan

## Recommendation

Use a plain `Containerfile` for compilation, keep flashing on the Windows host,
and treat the existing 2022 artifacts—not a live firmware dump—as the recovery
baseline.

The live-dump idea is understandable, but mostly overkill and potentially
unsafe. `dfu-programmer` supports dumping flash, but its documentation warns
that the default Atmel DFU security policy commonly prevents firmware
extraction. If dumping fails, do not erase the controller merely to enable
access: that would destroy the firmware we are trying to preserve.

Reference: [dfu-programmer manual](https://github.com/dfu-programmer/dfu-programmer/blob/master/docs/dfu-programmer.1)

## Existing recovery material

The archives already contain an unusually complete recovery baseline:

- A known firmware image from February 2022:
  `splitkb_kyria_rev1_slovak_kyria.hex`
- A historical build archive containing:
  - application HEX;
  - ELF with symbols;
  - linker map;
  - every object file;
  - the generated Vial keyboard definition;
  - complete compiler and linker flags.
- Exact historical compiler identity: `avr-gcc 8.4.0`.
- A 778 MB archive containing `qmk/vial-qmk.7z`.
- The GitHub fork and legacy branch:
  `KraXen72/vial-qmk-legacy:vial-avr-legacy`.
- A known-good Vial EEPROM/layout export:
  `vial_saves/v2_36_restore_accents2.vil`.
- Vial GUI 0.4.2 and the old QMK MSYS environment.

The firmware HEX contains executable behavior, including the `USERxx`
handlers. The `.vil` export contains the dynamic keymap stored in EEPROM. A
complete recovery therefore needs both.

## Options considered

| Approach | Verdict | Reason |
| --- | --- | --- |
| Dump firmware through the current DFU bootloader | Optional experiment only | Readout may be blocked; entering DFU interrupts the keyboard; never proceed to erase if dumping fails. |
| Dump through ISP using an external programmer | Reject for now | Requires opening or accessing both controllers and physical wiring; redundant given the archived HEX and ELF. |
| Recreate the old QMK MSYS environment on Windows | Keep as emergency fallback | Closest historical environment, but difficult to automate and preserve cleanly. |
| Use current Fedora AVR packages | Reject for the baseline | Modern compiler and binutils versions are unlikely to reproduce the old binary. |
| Wrap a custom image in a devcontainer | Reject for now | Adds editor and lifecycle orchestration that is not currently wanted. |
| Bake the firmware repository into the image | Reject | Makes source edits ephemeral or requires awkward persistence; source and toolchain belong in different layers. |
| Raw Containerfile with bind-mounted source | Recommend | Smallest understandable model; preserves a normal Git checkout and works with Docker or Podman. |
| GitHub Actions as the only build environment | Use only as a secondary verifier | Excellent for independent verification, but poor as the sole interactive development environment. |

## Repository shape

Keep firmware source, container configuration, scripts and reference metadata
in the legacy firmware repository:

```text
vial-qmk-legacy/
├── Containerfile
├── container/
│   ├── build
│   └── verify
├── keyboards/splitkb/kyria/keymaps/slovak_kyria/
├── reference/
│   ├── 2022-firmware.hex
│   ├── 2022-firmware.elf
│   ├── 2022-firmware.map
│   ├── v2_36-known-good.vil
│   └── SHA256SUMS
└── docs/
    └── recovery.md
```

Large binary recovery artifacts may be attached to a GitHub release or stored
with Git LFS. Their hashes and the small metadata needed to identify them
should remain directly in Git.

## Container design

The image should contain only the pinned toolchain:

- a Linux base image pinned by digest;
- `avr-gcc 8.4.0`;
- matching `avr-binutils`, `avr-libc`, Make and Python/QMK dependencies;
- a manifest recording every relevant version;
- no cloned mutable firmware repository;
- no USB passthrough;
- no Vial GUI.

The normal Git checkout is bind-mounted at `/workspace`. Approximate raw usage:

```powershell
podman build -t kyria-vial-legacy .
podman run --rm -v "${PWD}:/workspace" -w /workspace kyria-vial-legacy ./container/build
```

A small PowerShell wrapper should provide the normal interface:

```powershell
.\firmware.ps1 build
.\firmware.ps1 verify
```

QMK officially supports both Docker and Podman for compilation and recommends
keeping flashing outside the container on Windows.

Reference: [QMK Docker quick start](https://docs.qmk.fm/getting_started_docker)

## Build verification

The `verify` command should:

1. Start from a clean build directory.
2. Print all tool versions.
3. Compile `splitkb/kyria/rev1:slovak_kyria`.
4. Report application size and the configured bootloader limit.
5. Hash the resulting HEX.
6. Compare it with the archived reference.
7. If hashes differ, compare normalized flash contents and use the archived ELF
   and map to explain the difference.

There are two useful success levels:

1. **Functional reproduction:** the build fits, exposes the same Vial identity
   and custom keycodes, and behaves correctly.
2. **Bit-for-bit reproduction:** normalized Intel HEX contents exactly match the
   archived firmware.

Attempt bit-for-bit reproduction, but do not make it a prerequisite for safe
recovery. Embedded builds can differ because of source paths, timestamps,
generated version strings, linker ordering or dirty-tree metadata while still
being functionally identical.

The archived compiler identity, flags, ELF and map make an exact match
plausible. The central task is pinning the complete 2022 toolchain, not merely
checking out Vial QMK commit `bdbfe655`.

## Flashing and recovery boundary

Compilation belongs in the container. Flashing should remain native on Windows
using QMK Toolbox or `dfu-programmer`.

References:

- [QMK Docker quick start](https://docs.qmk.fm/getting_started_docker)
- [QMK Atmel DFU instructions](https://docs.qmk.fm/flashing)

Before any experimental flash:

1. Confirm the archived HEX files can be parsed.
2. Record their cryptographic hashes in Git.
3. Preserve `v2_36_restore_accents2.vil` alongside the matching firmware.
4. Verify the replacement build fits below the application limit implied by
   the 4 KiB Atmel DFU bootloader.
5. Flash only one half first.
6. Confirm it works and can reliably re-enter DFU before touching the other
   half.
7. Restore the `.vil` after flashing if EEPROM was cleared or is incompatible.

VIA and Vial use the dynamic keymap stored in EEPROM after initialization, so
the compiled default keymap may not immediately appear after flashing.

Reference: [QMK keymap FAQ](https://docs.qmk.fm/faq_keymap)

## Implementation plan

### Phase 1: establish the historical baseline

1. Extract the historical `vial-qmk.7z` into a temporary directory.
2. Establish its exact Git commit, submodule state, keymap source and dependency
   versions.
3. Compare it with `KraXen72/vial-qmk-legacy:vial-avr-legacy`.
4. Import anything missing and tag the exact baseline, for example
   `kyria-vial-2022-recovery`.
5. Hash and catalogue the archived HEX, ELF, map, object-tree archive and
   known-good `.vil` file.

### Phase 2: reproduce the toolchain

1. Build a minimal raw `Containerfile` pinned to the historical AVR toolchain.
2. Avoid the generic Fedora toolchain base initially: it introduces another
   moving part and likely lacks the exact historical AVR packages.
3. Add one canonical build script containing the firmware target.
4. Add a verification script that records versions, sizes and hashes.
5. Run two clean builds and compare hashes to prove the container is internally
   reproducible.

### Phase 3: compare with the historical firmware

1. Compare the new result with the 2022 HEX.
2. If different, normalize Intel HEX record ordering and metadata before
   comparing application bytes.
3. Use the archived map, ELF, flags and object files to identify remaining
   toolchain or source differences.
4. Document whether the result is bit-identical or only functionally
   equivalent.

### Phase 4: independent verification

1. Add a small GitHub Actions workflow using the same `Containerfile`.
2. Build from the pinned source revision.
3. Publish the resulting HEX, tool-version manifest and hashes as workflow
   artifacts or a tagged release.
4. Require the local and CI builds to match each other.

### Phase 5: optional live dump

Only consider this after the recovery baseline is complete:

1. Disconnect or disable anything that could accidentally invoke a flash or
   erase operation.
2. Connect and reset only one half into DFU mode.
3. Attempt the read-only `dfu-programmer ... dump` operation.
4. If access is denied, stop immediately.
5. Never issue `erase` as part of obtaining a backup.

ISP extraction should remain a last-resort forensic option, not part of the
normal workflow.

### Phase 6: future firmware changes

1. Make changes on a branch from the frozen legacy tag.
2. Build and verify without connecting the keyboard.
3. Preserve the known-good firmware and EEPROM export separately.
4. Flash only one half and test it fully.
5. Flash the second half only after the first can be recovered reliably.

## Final position

Building the reproducible environment is worthwhile. Dumping the live board is
not necessary for safety because the historical backup already contains more
useful recovery and diagnostic material than a raw flash dump would provide.
There is no reason to reflash the now-working keyboard merely to prove the
environment; the first real flash should happen only when a firmware change is
needed.
