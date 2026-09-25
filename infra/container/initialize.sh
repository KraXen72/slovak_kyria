#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="${KYRIA_PROJECT_ROOT:-/workspace}"
CONFIG_FILE="$PROJECT_ROOT/infra/container/versions.env"
BUILD_ID_PATCH="$PROJECT_ROOT/infra/container/patches/deterministic-build-id.patch"

if [[ ! -f "$CONFIG_FILE" ]]; then
    printf 'error: build contract not found: %s\n' "$CONFIG_FILE" >&2
    exit 1
fi

if [[ ! -f "$BUILD_ID_PATCH" ]]; then
    printf 'error: deterministic build patch not found: %s\n' "$BUILD_ID_PATCH" >&2
    exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG_FILE"

QMK_DIR="$PROJECT_ROOT/vial-qmk"
fresh_clone=0

if [[ -e "$QMK_DIR" && ! -e "$QMK_DIR/.git" ]]; then
    if [[ ! -d "$QMK_DIR" ]]; then
        printf 'error: %s exists but is not a Git checkout; refusing to remove it\n' "$QMK_DIR" >&2
        printf '       move it aside if it is disposable, then rerun the command\n' >&2
        exit 1
    fi

    shopt -s nullglob dotglob
    qmk_entries=("$QMK_DIR"/*)
    shopt -u nullglob dotglob
    if (( ${#qmk_entries[@]} > 0 )); then
        printf 'error: %s exists but is not a Git checkout; refusing to remove it\n' "$QMK_DIR" >&2
        printf '       move it aside if it is disposable, then rerun the command\n' >&2
        exit 1
    fi
fi

if [[ ! -e "$QMK_DIR/.git" ]]; then
    printf 'Cloning legacy Vial-QMK source (%s)...\n' "$VIAL_QMK_COMMIT"
    git clone --recurse-submodules \
        --branch "$VIAL_QMK_BRANCH" \
        --single-branch \
        "$VIAL_QMK_REPOSITORY" \
        "$QMK_DIR"
    fresh_clone=1
fi

if ! git -C "$QMK_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf 'error: %s is not a usable Git checkout\n' "$QMK_DIR" >&2
    exit 1
fi

actual_commit="$(git -C "$QMK_DIR" rev-parse HEAD)"
if [[ "$actual_commit" != "$VIAL_QMK_COMMIT" ]]; then
    if [[ "$fresh_clone" == 1 || "${KYRIA_ALLOW_QMK_MISMATCH:-0}" != "1" ]]; then
        printf 'error: the QMK checkout is not at the pinned commit\n' >&2
        printf '       expected: %s\n       actual:   %s\n' "$VIAL_QMK_COMMIT" "$actual_commit" >&2
        printf '       move the checkout/volume aside to recreate it\n' >&2
        printf '       or set KYRIA_ALLOW_QMK_MISMATCH=1 for an intentional local QMK fork\n' >&2
        exit 1
    fi
    printf 'warning: building an intentionally mismatched QMK checkout (%s)\n' "$actual_commit" >&2
fi

# Existing checkouts are intentionally not reset, fetched, or switched. This
# keeps local firmware-source work and commits safe across container rebuilds.
git -C "$QMK_DIR" submodule update --init --recursive

if [[ ! -d "$QMK_DIR/keyboards/splitkb/kyria/rev1" ]]; then
    printf 'error: pinned checkout has no Kyria rev1 keyboard definition\n' >&2
    exit 1
fi

# This legacy checkout otherwise emits a random build ID into every firmware
# image. Apply the small, versioned compatibility patch once and refuse to
# guess if a local edit conflicts with it.
if git -C "$QMK_DIR" apply --reverse --check "$BUILD_ID_PATCH" >/dev/null 2>&1; then
    :
elif git -C "$QMK_DIR" apply --check "$BUILD_ID_PATCH" >/dev/null 2>&1; then
    printf 'Applying deterministic firmware build-ID compatibility patch\n'
    git -C "$QMK_DIR" apply "$BUILD_ID_PATCH"
else
    printf 'error: cannot apply the deterministic build-ID patch safely\n' >&2
    printf '       inspect local changes to %s/util/build_id.py\n' "$QMK_DIR" >&2
    exit 1
fi

printf 'QMK checkout: %s\n' "$QMK_DIR"
printf 'QMK commit:   %s\n' "$actual_commit"

if [[ "${KYRIA_SHOW_QMK_STATUS:-0}" == "1" ]]; then
    # A full status scan is unusually slow on a checkout stored under
    # /mnt/c. Keep it opt-in because it is diagnostic, not part of building.
    git -C "$QMK_DIR" status --short --branch | sed -n '1,8p'
fi
