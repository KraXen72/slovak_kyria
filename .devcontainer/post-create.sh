#!/usr/bin/env bash
# .devcontainer/post-create.sh
# Runs once after the devcontainer is first created (not on every start).
# Re-run manually: bash .devcontainer/post-create.sh

set -euo pipefail

echo "==> installing system packages (qmk avr toolchain + dfu-programmer + uv)"
sudo dnf install -y \
    avr-gcc \
    avr-libc \
    avr-binutils \
    dfu-programmer \
    dfu-util \
    libusb1-devel \
    python3-pip \
    python3-devel \
    git \
    make \
    clang-tools-extra
sudo dnf clean all

echo "==> installing uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "==> installing QMK CLI"
pip3 install --user qmk

echo "==> running qmk setup (non-interactive, uses current workspace as QMK home)"
# We are already inside the vial-qmk checkout (workspaceFolder).
# qmk setup -H . initialises submodules and writes ~/.config/qmk/qmk.ini
qmk setup -H "$(pwd)" --yes 2>&1 | tail -20 || true

echo "==> installing helpercli deps (vial-to-keymap + keymap-drawer)"
# uv tool install makes these available as CLI commands.
uv tool install "git+https://github.com/Nisker/vial-to-keymap.git" || true
uv tool install keymap-drawer || true

echo ""
echo "==> post-create complete!"
echo "    compile:  qmk compile -kb splitkb/kyria/rev1 -km slovak_kyria"
echo "    flash:    ** run on HOST: dfu-programmer atmega32u4 flash <file.hex>"
echo "    vis:      uv run helpercli.py vis [--layer-names Base,Nav,Sym,Fn]"
echo ""
echo "    Vial GUI: run natively on HOST (see README — udev rules required)"
