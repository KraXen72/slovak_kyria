#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

if [[ "${KYRIA_DEV_CONTAINER:-0}" != "1" ]]; then
    exec "$SCRIPT_DIR/container-run.sh" bash infra/scripts/verify.sh "$@"
fi

# shellcheck disable=SC1090
source "$PROJECT_ROOT/infra/container/versions.env"

QMK_DIR="$PROJECT_ROOT/vial-qmk"
FIRMWARE_STEM="${KEYBOARD//\//_}_${KEYMAP}"
ARTIFACT="$PROJECT_ROOT/build/$FIRMWARE_STEM.hex"
KNOWN_GOOD="$PROJECT_ROOT/reference/known-good/$FIRMWARE_STEM.hex"
first_build="$(mktemp)"
trap 'rm -f -- "$first_build"' EXIT

printf 'Running a clean build, then repeating it to check determinism...\n'
bash "$PROJECT_ROOT/infra/container/initialize.sh"
bash "$PROJECT_ROOT/infra/container/sync-keymap.sh"
make -C "$QMK_DIR" clean
bash "$PROJECT_ROOT/infra/scripts/build.sh"
cp -- "$ARTIFACT" "$first_build"
first_hash="$(sha256sum "$first_build" | awk '{print $1}')"

make -C "$QMK_DIR" clean
bash "$PROJECT_ROOT/infra/scripts/build.sh"
second_hash="$(sha256sum "$ARTIFACT" | awk '{print $1}')"

if cmp -s "$first_build" "$ARTIFACT"; then
    printf 'Determinism: PASS (%s)\n' "$second_hash"
else
    printf 'Determinism: FAIL\n' >&2
    printf '  first clean build:  %s\n' "$first_hash" >&2
    printf '  second clean build: %s\n' "$second_hash" >&2
    exit 1
fi

if [[ -f "$KNOWN_GOOD" ]]; then
    if cmp -s "$KNOWN_GOOD" "$ARTIFACT"; then
        printf 'Historical comparison: PASS (%s)\n' "$KNOWN_GOOD"
    else
        printf 'Historical comparison: DIFFERENT (%s)\n' "$KNOWN_GOOD"
        printf '  current: %s\n' "$second_hash"
        printf '  known:   %s\n' "$(sha256sum "$KNOWN_GOOD" | awk '{print $1}')"
    fi
else
    printf 'Historical comparison: SKIPPED (no %s in this checkout)\n' "$KNOWN_GOOD"
fi
