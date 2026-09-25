# Kyria legacy firmware development plan

> Historical design record. The implemented interface is documented in
> [`../readme.md`](../readme.md); paths and commands in this document describe
> the earlier plan and are not the canonical setup.

## Goal

Create a low-maintenance development environment for the existing Kyria rev1
firmware on Elite-C/ATmega32U4 controllers. It must:

- build the legacy Vial-QMK firmware used with Vial GUI 0.4.2;
- preserve the historical firmware and working Vial layout as recovery assets;
- be comfortable to open in VS Code or enter through a shell;
- avoid repeatedly rebuilding the toolchain locally;
- let GitHub Actions build and publish the development image;
- keep firmware source changes in a normal Git repository.

We are not flashing or dumping either controller while creating this
environment. Any future operation that reads, erases or flashes a controller
requires explicit approval.

## Recommended design

Keep one project repository at `C:\Coding\keymap`. It contains the development
environment, documentation, build scripts, Vial exports and reference hashes.
On first container creation, an idempotent initialization script clones the
legacy Vial-QMK fork into a nested `vial-qmk/` directory.

```text
keymap/
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   └── workflows/
│       └── devcontainer-image.yml
├── container/
│   ├── Containerfile
│   └── initialize.sh
├── scripts/
│   ├── build.sh
│   └── verify.sh
├── reference/
│   ├── SHA256SUMS
│   └── README.md
├── vial-qmk/                 # generated, ignored by the outer repository
├── vial_saves/
├── README.md
└── firmware-dev-environment-plan.md
```

The outer `keymap` repository is mounted by the normal devcontainer workspace
bind mount. Therefore the nested `vial-qmk/` checkout and its Git history
persist on the host when the container is rebuilt or deleted. No named volume
or custom volume-management CLI is necessary.

The nested checkout remains its own Git repository and pushes firmware changes
to `KraXen72/vial-qmk-legacy`. The outer repository tracks only environment
infrastructure, documentation, reference metadata and Vial exports.

## Why this is not a published Template or Feature

This environment is only intended for the `keymap` project. A separately
published devcontainer Template would merely generate files that can live
directly in this repository. A custom Feature would split a single-purpose
toolchain across another repository and release process without improving the
daily workflow.

The repository-local `.devcontainer/devcontainer.json` provides the useful
parts of devcontainers directly:

- standard workspace mounting;
- VS Code integration;
- lifecycle hooks;
- a consistent non-root development user;
- a straightforward shell through the devcontainer CLI;
- optional editor extensions and settings.

If the legacy AVR toolchain later becomes useful to several unrelated
projects, it can be extracted into a Feature then. It should not be generalized
preemptively.

## Prebuilt development image

`container/Containerfile` defines the toolchain. GitHub Actions builds it and
publishes it to:

```text
ghcr.io/kraxen72/kyria-vial-legacy-dev:latest
```

The image can inherit from either:

1. the existing KraXen72 Fedora base image, if it already provides a suitable
   non-root user and common development tools; or
2. a normal Fedora 44 image, if using the custom base adds friction.

Choose whichever produces the smaller, clearer Containerfile after inspecting
the available base image. Exact bit-for-bit image reproducibility is not a
 requirement. Important firmware inputs should still be explicit enough
that the environment remains understandable and repairable.

The image should include:

- the AVR compiler and libraries required by the legacy build;
- Make and the normal QMK build dependencies;
- Python and the QMK CLI version compatible with the legacy tree;
- Git and basic shell utilities;
- tools needed by `build.sh` and `verify.sh`.

The historical build used `avr-gcc 8.4.0`. Prefer that version if practical.
If Fedora 44 supplies a different version, first test whether it builds the
firmware correctly before adding complicated compiler-pinning machinery.
Functional compatibility and recoverability matter more than forcing an exact
binary match.

The image should not contain the Vial-QMK source checkout. Shipping it in the
image would duplicate data, hide it beneath the workspace mount and make
ordinary firmware editing less natural.

The devcontainer configuration references the prebuilt GHCR image, so opening
the repository normally only pulls the image instead of rebuilding the
toolchain locally. Rebuilding the image locally remains available for work on
the Containerfile.

## Vial-QMK initialization

Use `onCreateCommand` to invoke `container/initialize.sh`. `onCreateCommand`
runs once when a devcontainer is created, which matches the one-time checkout
operation better than `postStartCommand`.

The initializer must be idempotent:

1. If `vial-qmk/.git` does not exist, clone
   `https://github.com/KraXen72/vial-qmk-legacy.git`.
2. Fetch and check out the preserved legacy commit or branch.
3. Initialize its submodules recursively.
4. Confirm that the expected Kyria keymap exists.
5. If the checkout already exists, leave its branch, commits and working tree
   untouched; only report its current state.

The exact source revision will be selected after comparing the historical
`vial-qmk.7z` archive with the `vial-avr-legacy` branch. Once established, use
a full commit SHA in the initializer. The branch name is useful for humans but
must not silently change the initial baseline.

A first-time clone taking up to approximately one minute is acceptable. It is
simpler than packaging the source inside a Feature or OCI image and immediately
provides a normal editable Git repository.

## Build and verification scripts

Avoid a project-specific Python/Click container-management CLI. Devcontainers
already manage creation, image pulling, workspace mounting and shell access.
Use small repository-local shell scripts for the firmware-specific operations.

`scripts/build.sh` should:

1. verify that `vial-qmk/` exists;
2. print the source commit and relevant tool versions;
3. compile `splitkb/kyria/rev1:slovak_kyria`;
4. copy the resulting HEX to a stable output directory in the outer workspace;
5. report firmware size and output hash.

`scripts/verify.sh` should:

1. perform a clean build;
2. compare the output with the known historical firmware;
3. report whether the result is byte-identical;
4. if it differs, report sizes and normalized firmware differences clearly.

A byte-identical build is desirable evidence, not an absolute requirement. A
non-identical build can still be accepted after establishing that it fits the
controller and retains the expected Vial identity, custom keycodes and other
required behavior. No such build will be flashed as part of this setup.

The scripts are the canonical commands used locally, from VS Code tasks and in
CI. Do not duplicate the keyboard/keymap target across several configuration
files if it can be defined once and reused.

## Daily workflow

Clone the outer repository and open it in VS Code. Choose **Dev Containers:
Reopen in Container**. VS Code pulls the prebuilt image, mounts the repository
and runs the one-time Vial-QMK initializer.

From the integrated terminal:

```bash
./scripts/build.sh
./scripts/verify.sh
```

Without VS Code:

```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . bash
```

Firmware development happens in `vial-qmk/`. Commit and push there using normal
Git commands. Changes to the environment, documentation or saved `.vil` files
are committed in the outer `keymap` repository.

VS Code tasks may expose **Build Kyria firmware** and **Verify Kyria firmware**
for convenience, but they must call the same shell scripts rather than contain
separate build logic.

## GitHub Actions

The outer repository should contain one workflow that:

1. builds `container/Containerfile`;
2. publishes the image to GHCR;
3. tags it with the source commit and `latest`;
4. reuses registry layer caching;
5. optionally runs `scripts/verify.sh` in the newly built image before
   publishing it.

The workflow is the normal image builder. Local image builds are primarily for
debugging changes to the Containerfile. This is the main reason for retaining
the devcontainer design: the expensive toolchain image is prepared remotely,
while the local machine only pulls it.

Do not make every firmware-source commit rebuild the development image. The
image should rebuild when the Containerfile, base image choice or toolchain
requirements change. Firmware builds themselves are cheap and run against the
bind-mounted checkout.

## Recovery material

The following existing material should be catalogued before any future flash:

- the February 2022 `splitkb_kyria_rev1_slovak_kyria.hex`;
- the historical ELF and linker map;
- the archived object tree and compiler flags;
- the historical `vial-qmk.7z` source archive;
- the working `vial_saves/v2_36_restore_accents2.vil` export;
- Vial GUI 0.4.2;
- cryptographic hashes for each retained artifact.

The firmware HEX contains executable behavior such as the `USERxx` handlers.
The `.vil` file contains the dynamic keymap stored in EEPROM. Both are needed
for complete recovery.

Large binaries can remain in the existing archive locations initially. Store
their paths, identities and hashes in `reference/README.md` and
`reference/SHA256SUMS`. They can later be attached to a GitHub release if a
single downloadable recovery package is useful.

## Implementation plan

### 1. Confirm prerequisites

- Install Podman in the intended WSL environment.
- Verify `podman version`, rootless operation and registry access.
- Install the devcontainer CLI and verify that it can use Podman.
- Account for the known Podman/devcontainer CLI startup race previously
  reported by KraXen72; do not build new project machinery around that bug
  unless it still reproduces.

### 2. Establish the source baseline

- Extract the historical `vial-qmk.7z` into a temporary location.
- Determine its Git commit and submodule state.
- Compare the historical `slovak_kyria` source with
  `KraXen72/vial-qmk-legacy:vial-avr-legacy`.
- Commit anything missing to the fork.
- Tag or otherwise record the full known-good baseline commit.

### 3. Catalogue recovery artifacts

- Hash the historical HEX, ELF, map, object archive, source archive and current
  known-good `.vil` file.
- Record which artifacts correspond to the known-good firmware.
- Validate that the HEX is structurally readable without connecting a
  controller.

### 4. Build the development image

- Choose the KraXen72 Fedora base or Fedora 44 after inspecting both.
- Implement the minimal Containerfile.
- Build and test it locally with Podman.
- Add the GitHub Actions workflow and publish the first GHCR image.
- Point `.devcontainer/devcontainer.json` at that image.

### 5. Initialize and build the firmware

- Add the idempotent `onCreateCommand` initializer.
- Create the devcontainer and confirm the nested checkout survives container
  rebuilds.
- Implement `build.sh` and compile the legacy target.
- Confirm the output fits the Elite-C application space.

### 6. Compare and debug

- Implement `verify.sh`.
- Compare repeated clean builds for internal consistency.
- Compare the new output with the historical HEX.
- If it differs, use the saved compiler flags, ELF, map and object files to
  identify the reason.
- Prefer a simple functionally equivalent build over excessive machinery whose
  only purpose is reproducing incidental binary differences.

### 7. Document the finished workflow

Write a concise README covering:

- prerequisite installation;
- opening the project in VS Code;
- creating and rebuilding the devcontainer;
- obtaining a shell without VS Code;
- building and verifying firmware;
- editing, committing and pushing the nested Vial-QMK checkout;
- locating build outputs and recovery artifacts;
- the explicit prohibition on dumping or flashing without approval.

## Explicitly out of scope

- Dumping firmware or EEPROM from either controller.
- Erasing or flashing either controller.
- USB device passthrough into the development container.
- Running Vial GUI inside the container.
- Migrating the keyboard to current QMK/Vial or ARM controllers.
- Publishing a generalized devcontainer Template or Feature before another
  real consumer exists.
