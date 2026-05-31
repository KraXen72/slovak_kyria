# vial-qmk devcontainer (Kyria rev1 / AVR)

## First-time host setup

### 1. Podman socket (Fedora)
```bash
systemctl --user enable --now podman.socket
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock
# add the export to your ~/.bashrc or ~/.zshrc
```

### 2. devcontainer CLI
```bash
npm install -g @devcontainers/cli
```

### 3. udev rules (one-time, on the HOST)
Needed for Vial GUI and `dfu-programmer` to see the keyboard:

```bash
# Vial GUI — Vial 0.4.2 magic number
export USER_GID=`id -g`; sudo --preserve-env=USER_GID sh -c 'echo "KERNEL==\"hidraw*\", SUBSYSTEM==\"hidraw\", ATTRS{serial}==\"*vial:f64c2b3c*\", MODE=\"0660\", GROUP=\"$USER_GID\", TAG+=\"uaccess\", TAG+=\"udev-acl\"" > /etc/udev/rules.d/59-vial.rules && udevadm control --reload && udevadm trigger'

# dfu-programmer / dfu-util (ATmega32U4 DFU bootloader)
export USER_GID=`id -g`; sudo --preserve-env=USER_GID sh -c 'echo "SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"2341\", MODE=\"0660\", GROUP=\"$USER_GID\", TAG+=\"uaccess\"" > /etc/udev/rules.d/60-dfu.rules && udevadm control --reload && udevadm trigger'
```

> If you previously had `99-vial.rules`, switch to `59-vial.rules` — required by
> recent kernel changes. See https://get.vial.today/manual/linux-udev.html

### 4. Vial GUI 0.4.2 (HOST, not container)
Download the AppImage from the [Vial releases page](https://github.com/vial-kb/vial-gui/releases/tag/v0.4.2).
```bash
chmod +x vial-v0.4.2.AppImage
./vial-v0.4.2.AppImage
```

---

## Daily workflow

### With dcman
```bash
dcman shell          # start container, open shell
dcman rebuild        # rebuild after .devcontainer.json changes
dcman kill           # stop container
```

### Without dcman
```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . bash
```

### Compile firmware (inside container)
```bash
qmk compile -kb splitkb/kyria/rev1 -km slovak_kyria
# output: .build/splitkb_kyria_rev1_slovak_kyria.hex
```

### Flash firmware (on HOST — not inside container)
The compiled `.hex` is in `.build/` inside the mounted workspace, so it
is directly accessible from the host at the same path.

Put the keyboard into DFU mode (press reset or use `QK_BOOT` key):
```bash
dfu-programmer atmega32u4 erase
dfu-programmer atmega32u4 flash .build/splitkb_kyria_rev1_slovak_kyria.hex
dfu-programmer atmega32u4 reset
```
Flash both halves (the Kyria is a split keyboard; flash each Elite-C separately).

---

## helpercli.py

```bash
uv run helpercli.py help

# common commands:
uv run helpercli.py fetchkeys                        # update keycodedb.json from QMK
uv run helpercli.py genkey                           # sync customKeycodes -> vial.json
uv run helpercli.py viltokey                         # .vil save -> C LAYOUT() (migration)
uv run helpercli.py vis --layer-names "Base,Nav,Sym,Fn"  # generate keymap.svg
```

`vis` requires the keyboard to be plugged in on the HOST with udev rules set up.
It invokes `vial-to-keymap` + `keymap draw` and writes `keymap.svg`.

---

## Git / repo setup

Your working state at container creation time:
- remote: `git@github.com:vial-kb/vial-qmk.git`
- branch: `vial`
- commit: `bdbfe655` (4 years old, last stable for your Elite-C setup)

**Recommended:** fork `vial-kb/vial-qmk` and create a `legacy-avr-bdbfe65` branch
so this exact state is permanently preserved under your own namespace:

```bash
# on host, in your vial-qmk checkout:
git remote add myfork git@github.com:<you>/vial-qmk.git
git checkout -b legacy-avr-bdbfe65
git push myfork legacy-avr-bdbfe65
```

---

## Notes

- **Vial GUI runs on the HOST** — GUI-in-container requires display forwarding
  which breaks the sandbox model. Run `vial-v0.4.2.AppImage` natively.
- **Flashing runs on the HOST** — USB passthrough into Podman containers is
  possible via `--device` but fragile; the `.hex` is in the mounted workspace
  so just flash from the host directly.
- **ARM migration path**: once you buy new RP2040 controllers (Elite-Pi, Liatris,
  or AliExpress RP2040 Pro Micro clones), create a new branch on your fork and
  port the keymap to current `vial-qmk main`. The AVR branch stays as a backup.
