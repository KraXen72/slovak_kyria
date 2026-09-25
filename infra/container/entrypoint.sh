#!/usr/bin/env bash
set -Eeuo pipefail

export KYRIA_DEV_CONTAINER=1

# The workspace is mounted by the host launcher or by the optional
# devcontainer configuration. Do not make the image unusable for diagnostics
# when it is started without that mount.
if [[ "${KYRIA_SKIP_INITIALIZE:-0}" != "1" && -f /workspace/infra/container/initialize.sh ]]; then
    bash /workspace/infra/container/initialize.sh
fi

exec "$@"
