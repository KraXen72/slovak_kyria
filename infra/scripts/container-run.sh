#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
# shellcheck disable=SC1090
source "$PROJECT_ROOT/infra/container/versions.env"

if ! command -v podman >/dev/null 2>&1; then
    printf 'error: Podman is required on the host. See readme.md for setup commands.\n' >&2
    exit 127
fi

use_tty=0
if [[ "${1:-}" == "--tty" ]]; then
    use_tty=1
    shift
fi

if [[ $# -eq 0 ]]; then
    set -- bash
fi

IMAGE_REF="${KYRIA_DEV_IMAGE_REF:-${DEV_IMAGE}@${DEV_IMAGE_DIGEST}}"
LOCAL_IMAGE_REF="${KYRIA_DEV_LOCAL_IMAGE_REF:-localhost/kyria-vial-legacy-dev:local}"

if ! podman image exists "$IMAGE_REF"; then
    printf 'Pulling %s...\n' "$IMAGE_REF"
    if ! podman pull "$IMAGE_REF"; then
        printf '\nThe prebuilt image is unavailable. Building the same image locally...\n'
        podman build \
            --file "$PROJECT_ROOT/infra/container/Containerfile" \
            --tag "$LOCAL_IMAGE_REF" \
            "$PROJECT_ROOT"
        IMAGE_REF="$LOCAL_IMAGE_REF"
    fi
fi

qmk_volume_args=()
use_qmk_volume="${KYRIA_USE_QMK_VOLUME:-auto}"
if [[ "$use_qmk_volume" == "1" || ( "$use_qmk_volume" == "auto" && "$PROJECT_ROOT" == /mnt/* ) ]]; then
    QMK_VOLUME_NAME="${KYRIA_QMK_VOLUME:-kyria-vial-qmk}"
    if ! podman volume exists "$QMK_VOLUME_NAME"; then
        podman volume create "$QMK_VOLUME_NAME" >/dev/null
    fi
    printf 'Using persistent Linux-side QMK volume: %s\n' "$QMK_VOLUME_NAME"
    qmk_volume_args+=(--volume "$QMK_VOLUME_NAME:/workspace/vial-qmk:Z")
fi

run_args=(
    run
    --rm
    --pull=never
    --userns=keep-id
    --user "$(id -u):$(id -g)"
    --env KYRIA_DEV_CONTAINER=1
    --env KYRIA_PROJECT_ROOT=/workspace
    --env QMK_HOME=/workspace/vial-qmk
    --env HOME=/tmp
    --volume "$PROJECT_ROOT:/workspace:Z"
    "${qmk_volume_args[@]}"
    --workdir /workspace
)

if [[ "$use_tty" == 1 ]]; then
    run_args+=(--interactive --tty)
fi

exec podman "${run_args[@]}" "$IMAGE_REF" "$@"
