# Slovak Kyria keymap and firmware

This repository is the editable project layer for a Kyria rev1 using the
legacy Vial-QMK AVR firmware. The editable keyboard source lives under
`firmware/`. The first build creates an ignored `vial-qmk/` checkout at the
pinned source revision and copies the source into it before compiling.

## Quick start from Linux or WSL

The commands below run in a Linux or WSL terminal. They do not run in
PowerShell or `cmd.exe`; WSL is the Windows host contract for this project.

Install the small host prerequisite set once:

```bash
# Fedora / Fedora WSL
sudo dnf install -y git podman

# Debian or Ubuntu / WSL (use this instead of the Fedora command)
sudo apt-get update
sudo apt-get install -y git podman
```

Check the installation:

```bash
git --version
podman --version
podman info
```

Then, from the cloned repository:

```bash
cd keymap
bash infra/scripts/build.sh
```

That command pulls the published GHCR development image. If the image is not
available yet, it automatically builds the same
`infra/container/Containerfile` locally. The first run also clones the pinned
QMK checkout and initializes its submodules.

When the repository is under `/mnt/c` in WSL, the launcher stores the generated
QMK checkout in the persistent Podman volume `kyria-vial-qmk` instead of the
Windows filesystem. This keeps repeated builds usable. On a native Linux path,
the checkout is bind-mounted from the ignored `vial-qmk/` directory by default.

## Daily development

Open the project in VS Code from WSL with `code .`, or use any editor on the
outer repository. The canonical build commands work either from the WSL host
or from the integrated terminal in the development container:

```bash
bash infra/scripts/dev-shell.sh

# inside the development shell:
bash infra/scripts/build.sh
bash infra/scripts/verify.sh
```

The VS Code Dev Containers extension can use `.devcontainer.json` as an
optional convenience, but installing the devcontainer CLI is not required.
The scripts above are the portable Podman interface.

Edit these outer-repository files:

- `firmware/keymap.c`, `firmware/config.h`, `firmware/rules.mk`,
  `firmware/my_slovak_keymap.h`, and `firmware/altlocal_keys.def` are the
  firmware source copied into the generated QMK keymap.
- `firmware/vial.json` and `firmware/vial_encoders.json` are Vial metadata.
- `vial_saves/` contains saved Vial layouts.

`tools/` contains optional keymap helpers, `infra/` contains the container and
launcher implementation, and `docs/` contains project notes. The generated
QMK checkout is an implementation cache, not the source of truth for the
keymap. On WSL `/mnt/c` it is inside the named Podman volume; use
`KYRIA_USE_QMK_VOLUME=0` if you deliberately need the checkout visible on the
host.

## Build outputs

Successful builds write these files under `build/`:

```text
build/splitkb_kyria_rev1_slovak_kyria.hex
build/splitkb_kyria_rev1_slovak_kyria.hex.sha256
build/splitkb_kyria_rev1_slovak_kyria.hex.info
```

The `.info` file records the keyboard, keymap, QMK repository and commit, QMK
CLI version, AVR compiler version, and firmware hash.

`verify.sh` performs two clean builds and compares them byte-for-byte. It also
compares a historical HEX if one is later added under
`reference/known-good/`; that artifact is not currently in this checkout.

## Recovery

The launcher uses the image in `infra/container/versions.env`. To update an already
cached image explicitly:

```bash
podman pull ghcr.io/kraxen72/kyria-vial-legacy-dev:latest
```

The GHCR package must be public for a new machine to pull it without a login.
If it is intentionally private, authenticate once with a GitHub token that
has `read:packages` permission:

```bash
podman login ghcr.io
```

If the Linux-side QMK volume is corrupt, preserve or export anything useful,
then remove only that named cache and let the next build clone a fresh copy:

```bash
podman volume rm kyria-vial-qmk
bash infra/scripts/build.sh
```

For a native Linux bind-mounted checkout, move `vial-qmk/` aside instead. The
initializer never resets, fetches, switches, or deletes an existing QMK
checkout. It verifies the pinned commit and leaves local QMK work alone.

## Helper CLI

The optional helper uses `uv` and is separate from the firmware build. Install
`uv` on the WSL/Linux host if you need it:

```bash
uv run tools/helpercli.py --help
uv run tools/helpercli.py fetchkeys
uv run tools/helpercli.py genkey
uv run tools/helpercli.py viltokey path/to/layout.vil
```

The visualization command talks to a connected keyboard and is not part of the
build or verification path. The helper always reads and writes project files
using their repository locations, regardless of the current directory.

## Repository layout

```text
firmware/     editable keyboard firmware and Vial metadata
tools/        optional keymap/recovery helpers
infra/        Podman image, pinned build contract, and launcher scripts
docs/         notes and design records
.github/      image publishing workflow
```

## Source and recovery references

The firmware baseline and missing historical artifacts are documented in
[`reference/README.md`](reference/README.md). The retained Vial export most
closely associated with the recovery notes is
[`vial_saves/v2_36_restore_accents2.vil`](vial_saves/v2_36_restore_accents2.vil).

This setup does not dump, erase, or flash either controller. Those operations
remain separate, hardware-facing work.

## Credits

This started as a Slovak typing keymap by [precondition](https://github.com/precondition),
with the alt-local layout work from [Eric Gebhart](https://github.com/EricGebhart).
