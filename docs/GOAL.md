# Project goal

## What this project should make easy

After a long break, I should be able to clone this repository on a Linux
machine or in WSL on Windows, follow a short set of README commands, and get a
working development shell for my Kyria keymap and firmware. I should not have
to remember old toolchain details, diagnose container setup, or reconstruct
which firmware source and settings belong together.

The setup may require installing a small number of host prerequisites. The
README must name them, give copyable setup and verification commands for both
supported hosts, and explain how to recover when a command fails.

## Acceptance criteria

- The same documented workflow works on Linux and Windows through WSL.
- Firmware source, keymap source, compiler/tool versions, and build settings
  are pinned or otherwise recorded so a build can be repeated later.
- A prebuilt OCI image is produced by GitHub Actions so a new machine does not
  need to build the toolchain locally.
- The firmware checkout is editable and persists across container recreation.
- One documented command opens the development shell; documented build and
  verification commands produce a named firmware artifact and its hash.
- The README explains the host prerequisites, first start, rebuild/recovery,
  Git workflow, output files, and where the known-good recovery files live.
- A later maintainer can tell which decisions and source revisions created a
  firmware artifact without relying on this conversation.

## Safety and scope

This work prepares and verifies firmware builds without connecting to either
controller. Reading EEPROM, dumping, erasing, or flashing a controller remains
out of scope and requires my explicit approval.

The current intended hardware is the Kyria rev1 with Elite-C / ATmega32U4
controllers and the legacy Vial workflow. A future ARM migration is separate
work.

## Decisions that still need evidence

- GitHub Actions and GHCR live in `KraXen72/slovak_kyria`; the active
  development branch is `firmware-dev-environment` and the image is
  `ghcr.io/kraxen72/kyria-vial-legacy-dev`.
- Confirm the exact firmware source revision and keymap contents against the
  retained legacy source archive and known-good firmware before calling a
  build baseline verified.
- The host interface is a small Linux/WSL prerequisite set plus the Podman
  launcher documented in the root README; VS Code Dev Containers remains an
  optional convenience.
