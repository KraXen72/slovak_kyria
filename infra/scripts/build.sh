#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

if [[ "${KYRIA_DEV_CONTAINER:-0}" != "1" ]]; then
    exec "$SCRIPT_DIR/container-run.sh" bash infra/scripts/build.sh "$@"
fi

# shellcheck disable=SC1090
source "$PROJECT_ROOT/infra/container/versions.env"

bash "$PROJECT_ROOT/infra/container/initialize.sh"
bash "$PROJECT_ROOT/infra/container/sync-keymap.sh"

QMK_DIR="$PROJECT_ROOT/vial-qmk"
FIRMWARE_STEM="${KEYBOARD//\//_}_${KEYMAP}"
QMK_HEX="$QMK_DIR/.build/$FIRMWARE_STEM.hex"
ARTIFACT_DIR="$PROJECT_ROOT/build"
ARTIFACT="$ARTIFACT_DIR/$FIRMWARE_STEM.hex"

printf '\nBuild contract\n'
printf '  keyboard:    %s\n' "$KEYBOARD"
printf '  keymap:      %s\n' "$KEYMAP"
printf '  qmk commit:  %s\n' "$(git -C "$QMK_DIR" rev-parse HEAD)"
printf '  qmk cli:     %s\n' "$(qmk --version 2>&1 | sed -n '1p')"
printf '  avr-gcc:     %s\n' "$(avr-gcc --version | sed -n '1p')"

if [[ "${KYRIA_CLEAN_BUILD:-0}" == "1" ]]; then
    make -C "$QMK_DIR" clean
fi

cd "$QMK_DIR"
QMK_HOME="$QMK_DIR" qmk compile -kb "$KEYBOARD" -km "$KEYMAP" -e SKIP_GIT=yes

if [[ ! -f "$QMK_HEX" ]]; then
    printf 'error: expected firmware was not produced: %s\n' "$QMK_HEX" >&2
    printf '       available HEX files:\n' >&2
    find "$QMK_DIR/.build" -maxdepth 1 -type f -name '*.hex' -print >&2
    exit 1
fi

mkdir -p "$ARTIFACT_DIR"
cp -- "$QMK_HEX" "$ARTIFACT"
sha256sum "$ARTIFACT" > "$ARTIFACT.sha256"
{
    printf 'keyboard=%s\n' "$KEYBOARD"
    printf 'keymap=%s\n' "$KEYMAP"
    printf 'qmk_repository=%s\n' "$VIAL_QMK_REPOSITORY"
    printf 'qmk_branch=%s\n' "$VIAL_QMK_BRANCH"
    printf 'qmk_commit=%s\n' "$(git -C "$QMK_DIR" rev-parse HEAD)"
    printf 'qmk_cli=%s\n' "$(qmk --version 2>&1 | sed -n '1p')"
    printf 'qmk_git_metadata=SKIP_GIT\n'
    printf 'build_id=0x00000000\n'
    printf 'avr_gcc=%s\n' "$(avr-gcc --version | sed -n '1p')"
    printf 'sha256=%s\n' "$(sha256sum "$ARTIFACT" | awk '{print $1}')"
} > "$ARTIFACT.info"

printf '\nFirmware: %s\n' "$ARTIFACT"
printf 'SHA-256: %s\n' "$(awk '{print $1}' "$ARTIFACT.sha256")"
