"""Helpers for generating and inspecting the outer Kyria keymap project."""

from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import click
import yaml
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
LAYOUTS_CONFIG = PROJECT_ROOT / "tools" / "layouts.yaml"
README_PATH    = PROJECT_ROOT / "readme.md"
ASSETS_DIR     = PROJECT_ROOT / "assets"

_DEFAULT_LAYOUT = "eurkey"
_OUTPUT_SUFFIXES = (".yaml", ".json", ".svg", ".png", ".meta.json")

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
    "RGB_MOD": "Mode+",
    "RGB_RMOD": "Mode-",
}

_ICON_LABELS = {
    "KC_UP": "$$icon_arrow_up$$",
    "KC_DOWN": "$$icon_arrow_down$$",
    "KC_LEFT": "$$icon_arrow_left$$",
    "KC_RIGHT": "$$icon_arrow_right$$",
    "KC_MPRV": "$$icon_skip_back$$",
    "KC_MPLY": "$$icon_play$$",
    "KC_MNXT": "$$icon_skip_forward$$",
    "KC_PAUSE": "$$icon_pause$$",
    "KC_VOLU": "$$icon_volume_high$$",
    "KC_VOLD": "$$icon_volume_low$$",
    "KC_MUTE": "$$icon_volume_mute$$",
}

_ICON_TEXT_LABELS = {
    "KC_UP": "Up",
    "KC_DOWN": "Down",
    "KC_LEFT": "Left",
    "KC_RIGHT": "Right",
    "KC_MPRV": "Prev",
    "KC_MPLY": "Play",
    "KC_MNXT": "Next",
    "KC_PAUSE": "Pause",
    "KC_VOLU": "Vol+",
    "KC_VOLD": "Vol-",
    "KC_MUTE": "Mute",
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
    "S": "S-",
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
    "Navigation": "Nav",
    "Nav / Fn": "Nav/Fn",
    "NavFn": "Nav",
    "Symbols": "Sym",
    "Function": "Fn",
    "RGB": "RGB",
    "RGB / Adjust": "RGB",
}

_LAYOUT_MODIFIERS = {
    "S": "shift",
    "LSFT": "shift",
    "RSFT": "shift",
    "RALT": "altgr",
    "ALGR": "altgr",
}

_LAYER_NAV_TOKENS = {
    "KC_UP",
    "KC_DOWN",
    "KC_LEFT",
    "KC_RIGHT",
    "KC_HOME",
    "KC_END",
    "KC_PGUP",
    "KC_PGDN",
    "KC_PAGEDOWN",
    "KC_PAGEUP",
    "KC_MPRV",
    "KC_MPLY",
    "KC_MNXT",
    "KC_PAUSE",
    "KC_VOLU",
    "KC_VOLD",
    "KC_MUTE",
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


@dataclass(frozen=True)
class LayoutResolver:
    """Resolve physical QMK keycodes against one host keyboard layout."""

    name: str
    label: str
    maps: dict[str, dict[str, str]]

    def resolve(self, token: str) -> str | None:
        """Return the layout character for a keycode expression, if defined."""
        parsed = _layout_token_parts(token)
        if parsed is None:
            return None
        modifiers, keycode = parsed
        if modifiers == frozenset():
            map_name = "base"
        elif modifiers == frozenset({"shift"}):
            map_name = "shift"
        elif modifiers == frozenset({"altgr"}):
            map_name = "altgr"
        elif modifiers == frozenset({"shift", "altgr"}):
            map_name = "shift_altgr"
        else:
            return None
        return self.maps.get(map_name, {}).get(keycode)


def _layout_token_parts(token: str) -> tuple[frozenset[str], str] | None:
    """Split nested shift/AltGr wrappers into modifiers and a physical keycode."""
    call_match = re.fullmatch(r"([A-Z0-9_]+)\((.*)\)", token)
    if call_match:
        operation, inner_token = call_match.groups()
        modifier = _LAYOUT_MODIFIERS.get(operation)
        if modifier is None:
            return None
        inner = _layout_token_parts(inner_token.strip())
        if inner is None:
            return None
        modifiers, keycode = inner
        return modifiers | {modifier}, keycode
    if token.startswith("KC_"):
        return frozenset(), token
    return None


def _load_layout_catalog() -> dict[str, LayoutResolver]:
    """Load layout maps and resolve their small inheritance graph."""
    try:
        raw = yaml.safe_load(LAYOUTS_CONFIG.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise click.ClickException(f"could not read layout configuration: {LAYOUTS_CONFIG}") from error

    definitions = raw.get("layouts") if isinstance(raw, dict) else None
    if not isinstance(definitions, dict):
        raise click.ClickException(f"layout configuration has no layouts map: {LAYOUTS_CONFIG}")

    resolved: dict[str, LayoutResolver] = {}

    def resolve(name: str, stack: tuple[str, ...] = ()) -> LayoutResolver:
        if name in resolved:
            return resolved[name]
        if name in stack:
            cycle = " -> ".join((*stack, name))
            raise click.ClickException(f"layout inheritance cycle: {cycle}")
        definition = definitions.get(name)
        if not isinstance(definition, dict):
            raise click.ClickException(f"layout {name!r} is not a mapping")

        maps: dict[str, dict[str, str]] = {}
        parent = definition.get("inherits")
        if parent:
            if not isinstance(parent, str):
                raise click.ClickException(f"layout {name!r} has an invalid parent")
            maps = {map_name: dict(values) for map_name, values in resolve(parent, (*stack, name)).maps.items()}

        own_maps = definition.get("maps", {})
        if not isinstance(own_maps, dict):
            raise click.ClickException(f"layout {name!r} has an invalid maps section")
        for map_name, values in own_maps.items():
            if not isinstance(values, dict):
                raise click.ClickException(f"layout {name!r} map {map_name!r} is not a mapping")
            maps.setdefault(str(map_name), {}).update(
                {str(key): str(value) for key, value in values.items() if value is not None}
            )

        label = definition.get("label", name)
        result = LayoutResolver(name=name, label=str(label), maps=maps)
        resolved[name] = result
        return result

    for name in definitions:
        resolve(str(name))
    return resolved


def _load_layout(layout_name: str) -> LayoutResolver | None:
    """Load a named host layout; ``none`` deliberately disables resolution."""
    if layout_name.casefold() == "none":
        return None
    catalog = _load_layout_catalog()
    try:
        return catalog[layout_name.casefold()]
    except KeyError as error:
        choices = ", ".join((*sorted(catalog), "none"))
        raise click.ClickException(f"unknown layout {layout_name!r}; choose one of: {choices}") from error


def _layout_choices() -> list[str]:
    """Return CLI layout choices from the declarative layout catalog."""
    return [*_load_layout_catalog(), "none"]


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
    """Map Vial custom-keycode tokens to the display names in ``vial.json``."""
    result: dict[str, str] = {}
    for index, entry in enumerate(definition.get("customKeycodes", [])):
        if not isinstance(entry, dict):
            continue
        short_name = entry.get("shortName")
        display_name = entry.get("name") or entry.get("shortName")
        if not display_name:
            continue
        display_name = str(display_name)
        result[f"USER{index:02d}"] = display_name
        if short_name:
            result[str(short_name)] = display_name
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


def _parse_layer_selection(value: str | None, layer_count: int) -> list[int]:
    """Parse a comma-separated layer selection and validate its indexes."""
    if value is None:
        return list(range(layer_count))
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


def _parse_layer_names(
    value: str | None,
    selected_layers: list[int],
    layer_count: int,
    default_names: list[str],
) -> list[str]:
    """Resolve names for the selected output layers and all layer references."""
    names = list(default_names)
    if layer_count > len(names):
        names.extend(f"Layer{index}" for index in range(len(names), layer_count))

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
    return f"Layer{index}"


def _layer_label(index: int, layer_names: list[str]) -> str:
    """Return a compact label for a layer key without changing layer headings."""
    name = _layer_name(index, layer_names)
    return _LAYER_LABELS.get(name, name)


def _flatten_layer_tokens(layer: list[list[Any]]) -> list[str]:
    """Return all string keycodes in one Vial layer for semantic classification."""
    return [
        value.strip()
        for row in layer
        for value in row
        if isinstance(value, str) and value.strip() not in {"-1", "KC_NO", "KC_TRNS", "XXXXXXX"}
    ]


def _infer_layer_names(layers: list[list[list[Any]]]) -> list[str]:
    """Infer useful headings from layer contents without relying on layer indexes."""
    names: list[str] = []
    used: set[str] = set()
    accent_pattern = re.compile(r"(?:ACUTE|CARON|UMLAU|DIA|CCIRC)")
    function_pattern = re.compile(r"(?:^|\()KC_F(?:[0-9]+)\)?$")
    symbol_pattern = re.compile(r"(?:KC_[0-9]|LSFT\(|S\(|KC_(?:GRAVE|MINUS|EQUAL|LBRACKET|RBRACKET|BSLASH))")

    for index, layer in enumerate(layers):
        tokens = _flatten_layer_tokens(layer)
        upper_tokens = [token.upper() for token in tokens]
        has_nav = bool(set(upper_tokens) & _LAYER_NAV_TOKENS)
        has_function = any(function_pattern.search(token) for token in upper_tokens)
        has_rgb = any(token.startswith("RGB_") for token in upper_tokens)
        has_accents = any(accent_pattern.search(token) for token in upper_tokens)
        has_symbols = any(symbol_pattern.search(token) for token in upper_tokens)

        if index == 0:
            candidate = "Base"
        elif has_accents:
            candidate = "Accents"
        elif has_rgb:
            candidate = "RGB"
        elif has_nav and has_function:
            candidate = "NavFn"
        elif has_nav:
            candidate = "Navigation"
        elif has_function:
            candidate = "Function"
        elif has_symbols:
            candidate = "Symbols"
        else:
            candidate = f"Layer{index}"

        if candidate in used:
            candidate = f"Layer{index}"
        names.append(candidate)
        used.add(candidate)
    return names


def _display_atom(
    token: str,
    custom_keycodes: dict[str, str],
    *,
    use_icons: bool = True,
) -> str:
    """Render a non-composite QMK/Vial token for keymap-drawer."""
    custom_name = custom_keycodes.get(token)
    if custom_name is None:
        user_match = re.fullmatch(r"USER(\d+)", token)
        if user_match:
            custom_name = custom_keycodes.get(f"USER{int(user_match.group(1)):02d}")
    if custom_name:
        token = custom_name

    if use_icons and token in _ICON_LABELS:
        return _ICON_LABELS[token]
    if token in _KEY_LABELS:
        return _KEY_LABELS[token]
    if token in _ICON_TEXT_LABELS:
        return _ICON_TEXT_LABELS[token]
    if token in _RGB_LABELS:
        return _RGB_LABELS[token]
    if token in _MODIFIER_LABELS:
        return _MODIFIER_LABELS[token]
    if token.startswith("KC_"):
        return token[3:].replace("_", " ").title()
    return token


def _pretty_decoded_keycode(value: str) -> str:
    """Wrap legacy decoder strings so nested modifiers fit inside a keycap."""
    match = re.fullmatch(r"(?P<outer>[A-Za-z]+)\+(?P<inner>[A-Za-z]+)\((?P<key>[^()]+)\)", value)
    if match is None:
        return value
    inner = {"GUI": "Gui", "CTRL": "Ctrl", "SHIFT": "Shift"}.get(
        match.group("inner").upper(),
        match.group("inner"),
    )
    return f"{match.group('outer')}+{inner}\n{match.group('key')}"


def _format_keycode(
    raw: Any,
    layer_names: list[str],
    custom_keycodes: dict[str, str],
    layout: LayoutResolver | None,
    *,
    use_icons: bool = True,
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
            tap = _format_keycode(
                decoded.get("t"),
                layer_names,
                custom_keycodes,
                layout,
                use_icons=use_icons,
            )
            hold = decoded.get("h")
            if isinstance(hold, str):
                hold_match = re.fullmatch(r"MO\((\d+)\)", hold)
                hold = (
                    _layer_label(int(hold_match.group(1)), layer_names)
                    if hold_match
                    else _display_atom(hold, custom_keycodes, use_icons=use_icons)
                )
            return {"t": tap, "h": hold}
        if isinstance(decoded, str):
            return _pretty_decoded_keycode(decoded)
        return decoded
    if not isinstance(raw, str):
        return str(raw)

    token = raw.strip()
    if layout is not None and (resolved := layout.resolve(token)) is not None:
        return resolved

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
                "t": _format_keycode(
                    arguments[1],
                    layer_names,
                    custom_keycodes,
                    layout,
                    use_icons=use_icons,
                ),
                "h": _layer_label(int(arguments[0]), layer_names),
            }

        if operation in {"MT"} and len(arguments) >= 2:
            modifier = _MODIFIER_LABELS.get(arguments[0], _display_atom(arguments[0], custom_keycodes))
            return {
                "t": _format_keycode(
                    arguments[1],
                    layer_names,
                    custom_keycodes,
                    layout,
                    use_icons=use_icons,
                ),
                "h": modifier,
            }

        if operation.endswith("_T") and len(arguments) == 1:
            modifier_name = operation.removesuffix("_T")
            modifier = _MODIFIER_LABELS.get(modifier_name, modifier_name)
            return {
                "t": _format_keycode(
                    arguments[0],
                    layer_names,
                    custom_keycodes,
                    layout,
                    use_icons=use_icons,
                ),
                "h": modifier,
            }

        if operation in _MODIFIER_WRAPPERS and arguments:
            inner = _format_keycode(
                arguments[0],
                layer_names,
                custom_keycodes,
                None,
                use_icons=False,
            )
            modifier_label = {
                "C": "Ctrl",
                "LCTL": "Ctrl",
                "RCTL": "Ctrl",
                "LALT": "Alt",
                "RALT": "AltGr",
                "S": "Shift",
                "LSFT": "Shift",
                "RSFT": "Shift",
                "LGUI": "Gui",
                "RGUI": "Gui",
                "SGUI": "Shift+Gui",
            }.get(operation)
            if modifier_label:
                return f"{modifier_label}\n{inner}"
            return f"{_MODIFIER_WRAPPERS[operation]}{inner}"

        rendered_arguments = [
            _format_keycode(
                argument,
                layer_names,
                custom_keycodes,
                layout,
                use_icons=use_icons,
            )
            for argument in arguments
        ]
        return f"{operation}({', '.join(str(argument) for argument in rendered_arguments)})"

    return _display_atom(token, custom_keycodes, use_icons=use_icons)


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
    layout: LayoutResolver | None,
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
            spec = _format_keycode(raw, layer_names, custom_keycodes, layout)
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
    default=None,
    help="Comma-separated Vial layer indexes to include; defaults to every save layer.",
)
@click.option(
    "--layer-names",
    default=None,
    help="Names for selected layers, or names for every layer in the save.",
)
@click.option(
    "-l",
    "--layout",
    "layout_name",
    type=click.Choice(_layout_choices(), case_sensitive=False),
    default=_DEFAULT_LAYOUT,
    show_default=True,
    help="Host layout used to resolve modified keycodes; use 'none' to keep raw labels.",
)
@click.option(
    "--output",
    "output_stem",
    default=ASSETS_DIR / "keymap_latest",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path stem for the YAML, JSON, SVG, PNG, and metadata files.",
)
def vis(
    vil_file: Path,
    layers: str | None,
    layer_names: str | None,
    layout_name: str,
    output_stem: Path,
):
    """Draw selected layers from a Vial save with keymap-drawer.

    The generated YAML, layout JSON, SVG, PNG, and metadata are kept together
    so the image can be regenerated later from the committed Vial save and
    tool lockfile.
    """
    result = _render_visualization(
        vil_file=vil_file,
        layers=layers,
        layer_names=layer_names,
        layout_name=layout_name,
        output_stem=output_stem,
    )
    click.echo(f"wrote {result['key_count']} physical keys across layers {result['layers']}")
    click.echo(f"done — {result['svg_path']}")
    click.echo(f"PNG — {result['png_path']}")


def _project_path(path: Path) -> Path:
    """Resolve helper input paths relative to the outer project when possible."""
    if path.is_absolute():
        return path
    project_path = PROJECT_ROOT / path
    if project_path.exists():
        return project_path
    return path.resolve()


def _project_relative(path: Path) -> str:
    """Return a repository-relative path, or an absolute path for external input."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _sha256_path(path: Path) -> str:
    """Return a file's SHA-256 without loading the whole file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _visualization_fingerprint(
    vil_file: Path,
    layout_name: str,
    selected_layers: list[int],
    selected_layer_names: list[str],
) -> str:
    """Hash every project input that can affect the generated visualization."""
    digest = hashlib.sha256()
    input_paths = [
        vil_file,
        VIAL_JSON,
        DRAW_CONFIG,
        LAYOUTS_CONFIG,
        Path(__file__).resolve(),
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "uv.lock",
    ]
    for path in input_paths:
        # Repository-relative names keep the manifest portable across clones;
        # absolute checkout paths would force every machine to rerender.
        digest.update(_project_relative(path).encode("utf-8"))
        digest.update(_sha256_path(path).encode("ascii"))
    digest.update(layout_name.encode("utf-8"))
    digest.update(json.dumps(selected_layers, separators=(",", ":")).encode("ascii"))
    digest.update(json.dumps(selected_layer_names, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


def _build_visualization_metadata(
    vil_file: Path,
    layout_name: str,
    selected_layers: list[int],
    selected_layer_names: list[str],
) -> dict[str, Any]:
    """Build the manifest used to skip redundant pre-commit renders."""
    source = _project_relative(vil_file)
    return {
        "version": 1,
        "source": source,
        "source_sha256": _sha256_path(vil_file),
        "layout": layout_name,
        "layers": selected_layers,
        "layer_names": selected_layer_names,
        "fingerprint": _visualization_fingerprint(
            vil_file,
            layout_name,
            selected_layers,
            selected_layer_names,
        ),
    }


def _write_png(svg_path: Path, png_path: Path) -> None:
    """Rasterize the generated SVG with the self-contained resvg wheel."""
    try:
        from affine import Affine
        from resvg import render, usvg
    except ImportError as error:
        raise click.ClickException(
            "PNG generation requires the locked 'resvg' helper dependency; run 'uv sync' first"
        ) from error

    try:
        options = usvg.Options.default()
        options.load_system_fonts()
        tree = usvg.Tree.from_str(svg_path.read_text(encoding="utf-8"), options)
        png_data = render(tree, Affine.identity()[:6])
        png_path.write_bytes(bytes(png_data))
    except Exception as error:  # resvg exposes backend-specific exception types
        raise click.ClickException(f"could not rasterize {svg_path.name} to PNG: {error}") from error


def _render_visualization(
    vil_file: Path,
    layers: str | None,
    layer_names: str | None,
    layout_name: str,
    output_stem: Path,
) -> dict[str, Any]:
    """Convert a Vial save into all committed visualization artifacts."""
    vil_file = _project_path(vil_file)
    _, vial_layers = _load_vial_layers(vil_file)
    selected_layers = _parse_layer_selection(layers, len(vial_layers))
    inferred_names = _infer_layer_names(vial_layers)
    all_layer_names = _parse_layer_names(
        layer_names,
        selected_layers,
        len(vial_layers),
        inferred_names,
    )
    selected_layer_names = [all_layer_names[index] for index in selected_layers]
    layout = _load_layout(layout_name)

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
        layout,
    )

    if not output_stem.is_absolute():
        output_stem = PROJECT_ROOT / output_stem
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_stem.with_suffix(".json")
    yaml_path = output_stem.with_suffix(".yaml")
    svg_path = output_stem.with_suffix(".svg")
    png_path = output_stem.with_suffix(".png")
    meta_path = output_stem.with_suffix(".meta.json")

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
    layout_description = layout.label if layout is not None else "none (raw keycodes)"
    yaml_text = (
        f"# Source Vial save: {_project_relative(vil_file)}\n"
        f"# Layout resolution: {layout_description}\n"
        + yaml_text
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

    _write_png(svg_path, png_path)
    metadata = _build_visualization_metadata(
        vil_file,
        layout.name if layout is not None else "none",
        selected_layers,
        selected_layer_names,
    )
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "key_count": len(matrix_keys),
        "layers": selected_layers,
        "layer_names": selected_layer_names,
        "source": vil_file,
        "svg_path": svg_path,
        "png_path": png_path,
        "meta_path": meta_path,
        "metadata": metadata,
    }


_README_VIS_START = "<!-- BEGIN GENERATED KEYMAP VISUALIZATION -->"
_README_VIS_END = "<!-- END GENERATED KEYMAP VISUALIZATION -->"


def _readme_visualization_section(source: Path, layer_names: list[str]) -> str:
    """Render the README block maintained by the pre-commit visualization hook."""
    source_name = _project_relative(source)
    labels = ", ".join(layer_names)
    return "\n".join(
        [
            _README_VIS_START,
            f"![Latest Vial save: {labels}](assets/keymap_latest.png)",
            "",
            "The image above is generated from",
            f"[`{source_name}`]({source_name}):",
            f"the {labels} layers are shown in that order.",
            _README_VIS_END,
        ]
    )


def _update_readme_visualization(source: Path, layer_names: list[str]) -> bool:
    """Replace the marked README image block and report whether it changed."""
    readme = README_PATH.read_text(encoding="utf-8")
    section = _readme_visualization_section(source, layer_names)
    pattern = re.compile(
        re.escape(_README_VIS_START) + r".*?" + re.escape(_README_VIS_END),
        flags=re.DOTALL,
    )
    updated, count = pattern.subn(section, readme, count=1)
    if count != 1:
        raise click.ClickException(
            f"README is missing the {_README_VIS_START} / {_README_VIS_END} markers"
        )
    if updated != readme:
        README_PATH.write_text(updated, encoding="utf-8")
    return updated != readme


def _metadata_is_current(meta_path: Path, expected: dict[str, Any], output_stem: Path) -> bool:
    """Return whether all generated files match the current visualization inputs."""
    try:
        actual = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        actual == expected
        and all(output_stem.with_suffix(suffix).is_file() for suffix in _OUTPUT_SUFFIXES[:-1])
        and meta_path.is_file()
    )


@cli.command("refresh-readme")
@click.option("--force", is_flag=True, help="Regenerate the image even when its manifest is current.")
@click.option(
    "-l",
    "--layout",
    "layout_name",
    type=click.Choice(_layout_choices(), case_sensitive=False),
    default=_DEFAULT_LAYOUT,
    show_default=True,
    help="Host layout used to resolve modified keycodes; use 'none' to keep raw labels.",
)
def refresh_readme(force: bool, layout_name: str) -> None:
    """Refresh README visualization from the alphabetically last Vial save."""
    source = _latest_vial_save()
    _, layers = _load_vial_layers(source)
    selected_layers = list(range(len(layers)))
    layer_names = _infer_layer_names(layers)
    normalized_layout = layout_name.casefold()
    output_stem = ASSETS_DIR / "keymap_latest"
    expected = _build_visualization_metadata(
        source,
        normalized_layout,
        selected_layers,
        layer_names,
    )
    meta_path = output_stem.with_suffix(".meta.json")

    if force or not _metadata_is_current(meta_path, expected, output_stem):
        result = _render_visualization(
            vil_file=source,
            layers=None,
            layer_names=None,
            layout_name=normalized_layout,
            output_stem=output_stem,
        )
        layer_names = result["layer_names"]
    else:
        click.echo("visualization is already up to date")

    changed = _update_readme_visualization(source, layer_names)
    click.echo(f"README visualization source: {source.name}")
    click.echo(f"README text {'updated' if changed else 'already current'}")


def _latest_vial_save() -> Path:
    """Return the alphabetically last committed Vial save, ignoring other files."""
    saves = sorted(VIALSAVES_DIR.glob("*.vil"), key=lambda path: path.name.casefold())
    if not saves:
        raise click.ClickException(f"no .vil files found in {VIALSAVES_DIR}")
    return saves[-1]


if __name__ == "__main__":
    cli()
