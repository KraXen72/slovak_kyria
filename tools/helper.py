"""Helpers for generating and inspecting the outer Kyria keymap project."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

import click

# Resolve project files from this script rather than the caller's working
# directory, so `uv run -m tools.helper ...` works from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIRMWARE_DIR = PROJECT_ROOT / "firmware"

# keyboard geometry (adapt if you change boards)
ROWS_PER_HALF = 4

# paths in the outer repository
VIALSAVES_DIR  = PROJECT_ROOT / "vial_saves"
KEYCODEDB_PATH = VIALSAVES_DIR / "keycode_db.json"
KEYMAP_C       = FIRMWARE_DIR / "keymap.c"
VIAL_JSON      = FIRMWARE_DIR / "vial.json"

# QMK keycode sources (pinned commit for reproducibility) 
_QMK_BASE = "https://rawcdn.githack.com/qmk/qmk_firmware/ca10e4d07579ae85c6720fdd3db3a0bfb5ebff36/quantum"
_KEYCODE_SOURCES = [
    # (url, seek_past_marker)
    (f"{_QMK_BASE}/keycode.h",        "Short names for ease of definition of keymap"),
    (f"{_QMK_BASE}/keycode_legacy.h", None),
]

# user mod-tap aliases — add yours here 
_MODTAP_DEFINES = [
    "#define CTL_ESC  MT(MOD_LCTL,KC_ESC)",
    "#define CTL_QUOT MT(MOD_RCTL,SK_SECT)",
    "#define ALT_ENT  MT(MOD_LALT,KC_ENT)",
]

# diacritic display suffixes for Slovak custom keycodes 
_DIACRITIC_SUFFIXES: list[tuple[str, str]] = [
    ("ACUTE", "´"),
    ("CARON", "v"),
    ("UMLAU", ".."),
    ("DIA",   ".."),
    ("CCIRC", "^"),
]


# shared helpers

def _parse_define_lines(raw_lines: list[str]) -> list[tuple[str, str]]:
    """Return (short, long) alias pairs from C #define lines, skipping comments."""
    pairs = []
    for line in raw_lines:
        if "#define" not in line or "//" in line or "/*" in line:
            continue
        parts = line[8:].split()
        if len(parts) >= 2:
            pairs.append((parts[0], parts[1]))
    return pairs


def _run(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    click.echo("$ " + " ".join(args))
    return subprocess.run(args, **kwargs)


# CLI

@click.group()
def cli():
    """Helpers for the outer Kyria keymap project."""


# genkey 

@cli.command()
def genkey():
    """Generate vial customKeycodes from keymap.c -> vial.json."""
    for p in (KEYMAP_C, VIAL_JSON):
        if not p.exists():
            raise click.ClickException(f"{p} not found")

    lines = KEYMAP_C.read_text(encoding="utf-8").splitlines()

    # locate the customKeycodes enum body
    start = next((i for i, l in enumerate(lines) if "customKeycodes" in l), None)
    if start is None:
        raise click.ClickException("customKeycodes enum not found in keymap.c")
    body = lines[start + 1:]
    end  = next((i for i, l in enumerate(body) if "};" in l), None)
    if end is None:
        raise click.ClickException("customKeycodes enum has no closing };")
    body = body[:end]

    keycodes = []
    for line in body:
        raw = line.replace(" ", "").split(",")[0]
        if not raw or "ALT_LOCAL_KEYS" in raw:
            continue

        display = raw
        for marker, suffix in _DIACRITIC_SUFFIXES:
            if marker in raw:
                display = raw.replace(marker, "") + suffix
                break

        keycodes.append({
            "name":      display,
            "title":     raw.replace("_", " "),
            "shortName": raw,
        })

    obj = json.loads(VIAL_JSON.read_text(encoding="utf-8"))
    obj["customKeycodes"] = keycodes
    VIAL_JSON.write_text(json.dumps(obj, indent=4, ensure_ascii=False), encoding="utf-8")
    click.echo(f"wrote {len(keycodes)} customKeycodes -> {VIAL_JSON}")


# fetchkeys 

@cli.command()
def fetchkeys():
    """Fetch QMK keycode aliases from GitHub -> vial_saves/keycode_db.json."""
    VIALSAVES_DIR.mkdir(exist_ok=True)
    lib: dict[str, str] = {}   # long_name -> short_alias

    for url, seek_marker in _KEYCODE_SOURCES:
        click.echo(f"fetching {url.rsplit('/', 1)[-1]}...")
        with urlopen(url) as f:
            lines = f.read().decode("utf-8").splitlines()

        if seek_marker:
            cut = next((i for i, l in enumerate(lines) if seek_marker in l), None)
            if cut is not None:
                lines = lines[cut:]

        for short, long in _parse_define_lines(lines):
            lib[long] = short

    for line in _MODTAP_DEFINES:
        pairs = _parse_define_lines([line])
        for short, long in pairs:
            lib[long] = short
    click.echo(f"merged {len(_MODTAP_DEFINES)} user mod-tap aliases")

    KEYCODEDB_PATH.write_text(json.dumps(lib, indent=4, ensure_ascii=False), encoding="utf-8")
    click.echo(f"wrote {len(lib)} aliases -> {KEYCODEDB_PATH}")


# viltokey 

@cli.command()
@click.argument("vil_file", type=click.Path(exists=True, path_type=Path))
def viltokey(vil_file: Path):
    """Convert a .vil vial save to C LAYOUT() blocks (stdout).

    Requires fetchkeys to have been run first (vial_saves/keycode_db.json).
    """
    if not KEYCODEDB_PATH.exists():
        raise click.ClickException("keycodedb.json not found — run 'fetchkeys' first")

    obj = json.loads(vil_file.read_text(encoding="utf-8"))
    lib = json.loads(KEYCODEDB_PATH.read_text(encoding="utf-8"))

    long_char_defines: list[str] = []

    def resolve(kc) -> str | None:
        if kc == -1:
            return None
        if kc == "KC_TRNS":
            return "_______"
        if kc == "KC_NO":
            return "XXXXXXX"
        kc = lib.get(kc, str(kc))
        kc = kc.replace("LSFT(", "S(")
        if len(kc) > 7:
            alias = f"CLI_X{len(long_char_defines):03d}"
            long_char_defines.append(f"#define {alias} {kc}")
            kc = alias
        return kc

    def row_str(row: list, reverse: bool) -> str:
        entries = (resolve(k) for k in (reversed(row) if reverse else row))
        return "".join(f"{k:<7}, " for k in entries if k is not None)

    for lch in long_char_defines:
        click.echo(lch)

    click.echo("// clang-format off")
    click.echo("const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {")
    for idx, layer in enumerate(obj["layout"]["layers"]):
        click.echo(f"    [{idx}] = LAYOUT(")
        rows: list[str] = []
        for i, row in enumerate(layer):
            if i < ROWS_PER_HALF:
                rows.append(row_str(row, False))
            else:
                rows[i - ROWS_PER_HALF] += row_str(row, True)
        for r in rows:
            click.echo("        " + r)
        click.echo("    ),")
        click.echo()
    click.echo("};")
    click.echo("// clang-format on")


# vis 

@cli.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument("vtk_args", nargs=-1, type=click.UNPROCESSED)
def vis(vtk_args: tuple[str, ...]):
    """Generate keymap.svg from a connected Vial keyboard.

    \b
    Pipeline:
      vial-to-keymap --output <repo>/keymap_vis [VTK_ARGS] -> keymap_vis.yaml
      keymap draw <repo>/keymap_vis.yaml                    -> keymap.svg

    All VTK_ARGS are forwarded verbatim to vial-to-keymap.

    \b
    Linux: udev rules must be configured first.
    See: https://get.vial.today/manual/linux-udev.html

    \b
    Examples:
      uv run -m tools.helper vis
      uv run -m tools.helper vis --layer-names Base,Nav,Sym,Fn
      uv run -m tools.helper vis --os-layout us-intl
    """
    visualization_base = PROJECT_ROOT / "keymap_vis"
    r = _run(["vial-to-keymap", "--output", str(visualization_base), *vtk_args])
    if r.returncode != 0:
        raise click.ClickException(
            "vial-to-keymap failed.\n"
            "  keyboard plugged in?  udev rules set up?  vial-to-keymap installed?"
        )

    yaml_file = PROJECT_ROOT / "keymap_vis.yaml"
    if not yaml_file.exists():
        raise click.ClickException(f"{yaml_file} missing — vial-to-keymap produced no output")

    svg_file = PROJECT_ROOT / "keymap.svg"
    with svg_file.open("w", encoding="utf-8") as out:
        r = _run(["keymap", "draw", str(yaml_file)], stdout=out)
    if r.returncode != 0:
        raise click.ClickException("keymap draw failed — is keymap-drawer installed?")

    click.echo(f"done — {svg_file}")


if __name__ == "__main__":
    cli()
