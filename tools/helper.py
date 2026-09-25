"""Helpers for generating and inspecting the outer Kyria keymap project."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import click
from vial_to_keymap.kle import PhysicalKey, parse_kle
from vial_to_keymap.output import build_layout_json, generate_yaml

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
DRAW_CONFIG    = PROJECT_ROOT / "tools" / "draw_config.yaml"
ASSETS_DIR     = PROJECT_ROOT / "assets"

_DEFAULT_LAYER_NAMES = ["Base", "Accents", "Nav", "Sym", "Function", "Adjust"]
_DEFAULT_SAVE_LAYERS = [0, 2, 3]

_KEY_LABELS = {
    "KC_ENTER": "Enter",
    "KC_ENT": "Enter",
    "KC_ESCAPE": "Esc",
    "KC_ESC": "Esc",
    "KC_BSPACE": "Bksp",
    "KC_BSPC": "Bksp",
    "KC_TAB": "Tab",
    "KC_SPACE": "Space",
    "KC_SPC": "Space",
    "KC_CAPSLOCK": "Caps",
    "KC_CAPS": "Caps",
    "KC_DELETE": "Del",
    "KC_DEL": "Del",
    "KC_PSCREEN": "PrtSc",
    "KC_PSCR": "PrtSc",
    "KC_SCROLLLOCK": "ScrLk",
    "KC_SLCK": "ScrLk",
    "KC_PAGEUP": "PgUp",
    "KC_PGUP": "PgUp",
    "KC_PAGEDOWN": "PgDn",
    "KC_PGDOWN": "PgDn",
    "KC_PGDN": "PgDn",
    "KC_LCTRL": "Ctrl",
    "KC_RCTRL": "Ctrl",
    "KC_LCTL": "Ctrl",
    "KC_RCTL": "Ctrl",
    "KC_LSHIFT": "SFT",
    "KC_RSHIFT": "SFT",
    "KC_LSFT": "SFT",
    "KC_RSFT": "SFT",
    "KC_LALT": "Alt",
    "KC_RALT": "AltGr",
    "KC_LGUI": "GUI",
    "KC_RGUI": "GUI",
    "KC_SCOLON": ";",
    "KC_SCLN": ";",
    "KC_QUOTE": "'",
    "KC_QUOT": "'",
    "KC_COMMA": ",",
    "KC_COMM": ",",
    "KC_DOT": ".",
    "KC_SLASH": "/",
    "KC_SLSH": "/",
    "KC_GRAVE": "`",
    "KC_GRV": "`",
    "KC_MINUS": "-",
    "KC_MINS": "-",
    "KC_EQUAL": "=",
    "KC_EQL": "=",
    "KC_LBRACKET": "[",
    "KC_LBRC": "[",
    "KC_RBRACKET": "]",
    "KC_RBRC": "]",
    "KC_BSLASH": "\\",
    "KC_BSLS": "\\",
    "KC_UP": "Up",
    "KC_DOWN": "Down",
    "KC_LEFT": "Left",
    "KC_RIGHT": "Right",
    "KC_HOME": "Home",
    "KC_END": "End",
    "KC_INSERT": "Ins",
    "KC_INS": "Ins",
    "KC_VOLU": "Vol+",
    "KC_VOLD": "Vol-",
    "KC_MUTE": "Mute",
    "KC_MPLY": "Play",
    "KC_MPRV": "Prev",
    "KC_MNXT": "Next",
}

_RGB_LABELS = {
    "RGB_TOG": "RGB",
    "RGB_SAI": "Sat+",
    "RGB_SAD": "Sat-",
    "RGB_HUI": "Hue+",
    "RGB_HUD": "Hue-",
    "RGB_VAI": "Bright+",
    "RGB_VAD": "Bright-",
    "RGB_M_P": "Mode+",
    "RGB_M_R": "Mode-",
    "RGB_M_SW": "Mode",
}

_MODIFIER_LABELS = {
    "C": "Ctrl",
    "CTRL": "Ctrl",
    "LCTL": "Ctrl",
    "RCTL": "Ctrl",
    "MOD_LCTL": "Ctrl",
    "MOD_RCTL": "Ctrl",
    "S": "SFT",
    "LSFT": "SFT",
    "RSFT": "SFT",
    "MOD_LSFT": "SFT",
    "MOD_RSFT": "SFT",
    "A": "Alt",
    "LALT": "Alt",
    "RALT": "AltGr",
    "MOD_LALT": "Alt",
    "MOD_RALT": "AltGr",
    "G": "GUI",
    "LGUI": "GUI",
    "RGUI": "GUI",
    "MOD_LGUI": "GUI",
    "MOD_RGUI": "GUI",
}

_MODIFIER_WRAPPERS = {
    "C": "C-",
    "LCTL": "C-",
    "RCTL": "C-",
    "LALT": "A-",
    "RALT": "AG-",
    "LSFT": "S-",
    "RSFT": "S-",
    "LGUI": "G-",
    "RGUI": "G-",
    "SGUI": "SG-",
}

_LAYER_LABELS = {
    "Accents": "Acc",
    "Function": "Fn",
    "Adjust": "Adj",
}

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


def _split_call_arguments(raw: str) -> list[str]:
    """Split the arguments inside a QMK keycode call without breaking nesting."""
    args: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(raw):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(raw[start:index].strip())
            start = index + 1
    args.append(raw[start:].strip())
    return args


def _load_custom_keycodes(definition: dict[str, Any]) -> dict[str, str]:
    """Map Vial USERnn tokens to the symbolic names in ``vial.json``."""
    result: dict[str, str] = {}
    for index, entry in enumerate(definition.get("customKeycodes", [])):
        if not isinstance(entry, dict):
            continue
        short_name = entry.get("shortName")
        if short_name:
            result[f"USER{index:02d}"] = str(short_name)
    return result


def _normalise_vial_layout_tags(layout_rows: list[Any]) -> list[Any]:
    """Make legacy Vial layout-option tags consumable by the geometry parser.

    This keyboard definition stores tags in an older label slot, while the
    pinned parser reads the newer slot. It also has four independent thumb
    variant groups. Mapping every group to parser variant zero lets the
    parser retain option zero and discard each option-one alternate without
    disturbing the Vial layout cursor positions.
    """
    normalised: list[Any] = []
    tag_pattern = re.compile(r"^\d+,\d+$")

    for row in layout_rows:
        new_row: list[Any] = []
        for item in row:
            if not isinstance(item, str):
                new_row.append(item)
                continue

            labels = item.split("\n")
            tag_index = None
            for candidate in (8, 3):
                if candidate < len(labels) and tag_pattern.fullmatch(labels[candidate].strip()):
                    tag_index = candidate
                    break
            if tag_index is None:
                new_row.append(item)
                continue

            _, option = (int(part) for part in labels[tag_index].split(","))
            if len(labels) <= 8:
                labels.extend([""] * (9 - len(labels)))
            labels[8] = f"0,{option}"
            new_row.append("\n".join(labels))
        normalised.append(new_row)

    return normalised


def _load_physical_keys(definition: dict[str, Any]) -> list[PhysicalKey]:
    """Read the default physical Kyria layout and reject duplicate matrix keys."""
    try:
        layout_rows = definition["layouts"]["keymap"]
    except (KeyError, TypeError) as error:
        raise click.ClickException("firmware/vial.json has no layouts.keymap definition") from error

    physical_keys = parse_kle(_normalise_vial_layout_tags(layout_rows), default_layout_index=0)
    matrix_keys = [key for key in physical_keys if not key.is_encoder]
    addresses = [(key.row, key.col) for key in matrix_keys]
    duplicates = sorted({address for address in addresses if addresses.count(address) > 1})
    if not matrix_keys:
        raise click.ClickException("firmware/vial.json produced no matrix keys")
    if duplicates:
        formatted = ", ".join(f"{row},{col}" for row, col in duplicates)
        raise click.ClickException(f"physical layout contains duplicate matrix positions: {formatted}")
    return physical_keys


def _load_vial_layers(vil_file: Path) -> tuple[dict[str, Any], list[list[list[Any]]]]:
    """Load both current and older Vial save-file layout shapes."""
    try:
        save = json.loads(vil_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise click.ClickException(f"invalid Vial save: {vil_file}") from error

    layout = save.get("layout")
    if isinstance(layout, list):
        layers = layout
    elif isinstance(layout, dict) and isinstance(layout.get("layers"), list):
        layers = layout["layers"]
    else:
        raise click.ClickException("Vial save has no supported layout or layout.layers array")

    if not all(isinstance(layer, list) for layer in layers):
        raise click.ClickException("Vial save contains a malformed layer array")
    return save, layers


def _parse_layer_selection(value: str, layer_count: int) -> list[int]:
    """Parse a comma-separated layer selection and validate its indexes."""
    try:
        indexes = [int(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as error:
        raise click.ClickException(f"invalid layer selection: {value!r}") from error
    if not indexes or any(index < 0 or index >= layer_count for index in indexes):
        raise click.ClickException(
            f"layers must be valid indexes from 0 to {layer_count - 1}: {value!r}"
        )
    if len(set(indexes)) != len(indexes):
        raise click.ClickException(f"layers must not contain duplicates: {value!r}")
    return indexes


def _parse_layer_names(value: str | None, selected_layers: list[int], layer_count: int) -> list[str]:
    """Resolve names for the selected output layers and all layer references."""
    names = list(_DEFAULT_LAYER_NAMES)
    if layer_count > len(names):
        names.extend(f"Layer_{index}" for index in range(len(names), layer_count))

    if value is None:
        return names

    requested = [part.strip() for part in value.split(",") if part.strip()]
    if len(requested) == len(selected_layers):
        for index, name in zip(selected_layers, requested):
            names[index] = name
        return names
    if len(requested) == layer_count:
        return requested
    raise click.ClickException(
        "--layer-names must contain one name per selected layer "
        f"({len(selected_layers)}) or one per save layer ({layer_count})"
    )


def _layer_name(index: int, layer_names: list[str]) -> str:
    """Return a display name for a layer index, including unknown future layers."""
    if 0 <= index < len(layer_names):
        return layer_names[index]
    return f"Layer_{index}"


def _layer_label(index: int, layer_names: list[str]) -> str:
    """Return a compact label for a layer key without changing layer headings."""
    name = _layer_name(index, layer_names)
    return _LAYER_LABELS.get(name, name)


def _display_atom(token: str, custom_keycodes: dict[str, str]) -> str:
    """Render a non-composite QMK/Vial token for keymap-drawer."""
    custom_name = custom_keycodes.get(token)
    if custom_name is None:
        user_match = re.fullmatch(r"USER(\d+)", token)
        if user_match:
            custom_name = custom_keycodes.get(f"USER{int(user_match.group(1)):02d}")
    if custom_name:
        token = custom_name

    if token in _KEY_LABELS:
        return _KEY_LABELS[token]
    if token in _RGB_LABELS:
        return _RGB_LABELS[token]
    if token in _MODIFIER_LABELS:
        return _MODIFIER_LABELS[token]
    if token.startswith("KC_"):
        return token[3:].replace("_", " ").title()
    return token


def _format_keycode(
    raw: Any,
    layer_names: list[str],
    custom_keycodes: dict[str, str],
) -> str | dict[str, Any] | None:
    """Convert a Vial save keycode into a compact keymap-drawer key spec."""
    if raw is None or raw == -1 or raw in ("-1", "KC_NO", "XXXXXXX"):
        return None
    if raw in ("KC_TRNS", "_______"):
        return {"type": "trans"}
    if isinstance(raw, int):
        # Current Vial exports use symbolic strings, but older exports may
        # contain protocol integers.  Keep those readable instead of failing.
        from vial_to_keymap.keycodes import decode_keycode

        decoded = decode_keycode(raw)
        if isinstance(decoded, dict):
            tap = _format_keycode(decoded.get("t"), layer_names, custom_keycodes)
            hold = decoded.get("h")
            if isinstance(hold, str):
                hold_match = re.fullmatch(r"MO\((\d+)\)", hold)
                hold = (
                    _layer_label(int(hold_match.group(1)), layer_names)
                    if hold_match
                    else _display_atom(hold, custom_keycodes)
                )
            return {"t": tap, "h": hold}
        return decoded
    if not isinstance(raw, str):
        return str(raw)

    token = raw.strip()
    call_match = re.fullmatch(r"([A-Z0-9_]+)\((.*)\)", token)
    if call_match:
        operation = call_match.group(1)
        arguments = _split_call_arguments(call_match.group(2))

        if operation in {"MO", "TO", "DF", "TG", "OSL", "TT", "PDF"} and arguments:
            try:
                target = int(arguments[0])
            except ValueError:
                target = None
            if target is not None:
                target_name = _layer_label(target, layer_names)
                if operation == "MO":
                    return {"t": target_name, "type": "held"}
                if operation in {"TO", "DF"}:
                    return target_name
                return f"{operation}({target_name})"

        if operation == "LT" and len(arguments) >= 2:
            return {
                "t": _format_keycode(arguments[1], layer_names, custom_keycodes),
                "h": _layer_label(int(arguments[0]), layer_names),
            }

        if operation in {"MT"} and len(arguments) >= 2:
            modifier = _MODIFIER_LABELS.get(arguments[0], _display_atom(arguments[0], custom_keycodes))
            return {
                "t": _format_keycode(arguments[1], layer_names, custom_keycodes),
                "h": modifier,
            }

        if operation.endswith("_T") and len(arguments) == 1:
            modifier_name = operation.removesuffix("_T")
            modifier = _MODIFIER_LABELS.get(modifier_name, modifier_name)
            return {
                "t": _format_keycode(arguments[0], layer_names, custom_keycodes),
                "h": modifier,
            }

        if operation in _MODIFIER_WRAPPERS and arguments:
            inner = _format_keycode(arguments[0], layer_names, custom_keycodes)
            return f"{_MODIFIER_WRAPPERS[operation]}{inner}"

        rendered_arguments = [
            _format_keycode(argument, layer_names, custom_keycodes)
            for argument in arguments
        ]
        return f"{operation}({', '.join(str(argument) for argument in rendered_arguments)})"

    return _display_atom(token, custom_keycodes)


def _held_layer(raw: Any) -> int | None:
    """Return the layer held by a momentary-layer keycode, if any."""
    if isinstance(raw, str):
        match = re.fullmatch(r"MO\((\d+)\)", raw.strip())
        return int(match.group(1)) if match else None
    if isinstance(raw, int):
        from vial_to_keymap.keycodes import get_held_layer

        return get_held_layer(raw, vial_protocol=6)
    return None


def _save_layer_keys(
    layers: list[list[list[Any]]],
    physical_keys: list[PhysicalKey],
    selected_layers: list[int],
    layer_names: list[str],
    custom_keycodes: dict[str, str],
) -> list[list[str | dict[str, Any] | None]]:
    """Build display keys in the same physical order as the Vial layout."""
    matrix_keys = [key for key in physical_keys if not key.is_encoder]
    held_positions: dict[int, set[int]] = {}
    for position, key in enumerate(matrix_keys):
        for layer in layers:
            if key.row < len(layer) and key.col < len(layer[key.row]):
                target = _held_layer(layer[key.row][key.col])
                if target is not None:
                    held_positions.setdefault(target, set()).add(position)

    result: list[list[str | dict[str, Any] | None]] = []
    for layer_index in selected_layers:
        layer = layers[layer_index]
        output: list[str | dict[str, Any] | None] = []
        for position, key in enumerate(matrix_keys):
            if key.row < 0 or key.col < 0 or key.row >= len(layer) or key.col >= len(layer[key.row]):
                output.append(None)
                continue
            raw = layer[key.row][key.col]
            spec = _format_keycode(raw, layer_names, custom_keycodes)
            if spec == {"type": "trans"} and position in held_positions.get(layer_index, set()):
                spec = {"type": "held"}
            output.append(spec)
        result.append(output)
    return result


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


@cli.command("vis")
@click.argument("vil_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--layers",
    default=",".join(str(index) for index in _DEFAULT_SAVE_LAYERS),
    show_default=True,
    help="Comma-separated Vial layer indexes to include in the image.",
)
@click.option(
    "--layer-names",
    default=None,
    help="Names for selected layers, or names for every layer in the save.",
)
@click.option(
    "--output",
    "output_stem",
    default=ASSETS_DIR / "keymap_latest",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path stem for the YAML, JSON, and SVG files.",
)
def vis(vil_file: Path, layers: str, layer_names: str | None, output_stem: Path):
    """Draw selected layers from a Vial save with keymap-drawer.

    The generated YAML and layout JSON are kept next to the SVG so the image
    can be regenerated later from the committed Vial save and tool lockfile.
    """
    save, vial_layers = _load_vial_layers(vil_file)
    selected_layers = _parse_layer_selection(layers, len(vial_layers))
    all_layer_names = _parse_layer_names(layer_names, selected_layers, len(vial_layers))
    selected_layer_names = [all_layer_names[index] for index in selected_layers]

    try:
        definition = json.loads(VIAL_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise click.ClickException(f"invalid keyboard definition: {VIAL_JSON}") from error

    physical_keys = _load_physical_keys(definition)
    matrix = definition.get("matrix", {})
    rows = matrix.get("rows")
    cols = matrix.get("cols")
    matrix_keys = [key for key in physical_keys if not key.is_encoder]
    if isinstance(rows, int) and isinstance(cols, int):
        invalid = [key for key in matrix_keys if not (0 <= key.row < rows and 0 <= key.col < cols)]
        if invalid:
            raise click.ClickException("physical layout contains a key outside the Vial matrix")

    custom_keycodes = _load_custom_keycodes(definition)
    layer_keys = _save_layer_keys(
        vial_layers,
        physical_keys,
        selected_layers,
        all_layer_names,
        custom_keycodes,
    )

    if not output_stem.is_absolute():
        output_stem = PROJECT_ROOT / output_stem
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_stem.with_suffix(".json")
    yaml_path = output_stem.with_suffix(".yaml")
    svg_path = output_stem.with_suffix(".svg")

    layout_json = build_layout_json(physical_keys)
    json_path.write_text(json.dumps(layout_json, indent=2), encoding="utf-8")
    yaml_text = generate_yaml(
        keyboard_name=str(definition.get("name", "Kyria")),
        physical_keys=physical_keys,
        layer_keys=layer_keys,
        layer_names=selected_layer_names,
        layout_json_path=json_path.name,
    ).replace(
        "# Generated by vial-to-keymap – edit layer names as desired.",
        "# Generated by tools.helper for keymap-drawer.",
    )
    yaml_path.write_text(
        yaml_text,
        encoding="utf-8",
    )

    result = _run(
        [
            "keymap",
            "-c",
            str(DRAW_CONFIG),
            "draw",
            str(yaml_path),
            "-o",
            str(svg_path),
        ],
        cwd=output_stem.parent,
    )
    if result.returncode != 0:
        raise click.ClickException("keymap draw failed — is keymap-drawer installed?")

    click.echo(f"wrote {len(matrix_keys)} physical keys across layers {selected_layers}")
    click.echo(f"done — {svg_path}")


if __name__ == "__main__":
    cli()
