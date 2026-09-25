#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="${KYRIA_PROJECT_ROOT:-/workspace}"
# shellcheck disable=SC1090
source "$PROJECT_ROOT/infra/container/versions.env"

FIRMWARE_DIR="$PROJECT_ROOT/firmware"
QMK_DIR="$PROJECT_ROOT/vial-qmk"
TARGET_DIR="$QMK_DIR/keyboards/splitkb/kyria/keymaps/$KEYMAP"

required_files=(
    keymap.c
    config.h
    rules.mk
    my_slovak_keymap.h
    altlocal_keys.def
)
optional_files=(
    vial.json
    vial_encoders.json
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$FIRMWARE_DIR/$file" ]]; then
        printf 'error: required keymap source is missing: %s\n' "$FIRMWARE_DIR/$file" >&2
        exit 1
    fi
done

if [[ ! -d "$QMK_DIR/.git" ]]; then
    printf 'error: %s is not initialized; run infra/container/initialize.sh first\n' "$QMK_DIR" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

for file in "${required_files[@]}" "${optional_files[@]}"; do
    if [[ -f "$FIRMWARE_DIR/$file" ]]; then
        cp -- "$FIRMWARE_DIR/$file" "$TARGET_DIR/$file"
    fi
done

# This marker makes the generated nature of the nested keymap obvious when
# browsing the QMK checkout from a shell or an editor.
printf 'Generated from %s at %s\n' "$PROJECT_ROOT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$TARGET_DIR/.outer-keymap-source"
