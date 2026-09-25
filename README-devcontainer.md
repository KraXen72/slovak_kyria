# Optional VS Code devcontainer

The canonical interface is the Podman launcher documented in
[`readme.md`](readme.md):

```bash
bash infra/scripts/build.sh
bash infra/scripts/dev-shell.sh
```

If the VS Code Dev Containers extension is already installed, **Reopen in
Container** uses `.devcontainer.json` and the same published image. The outer
repository is mounted at `/workspace`, and the generated QMK checkout uses the
persistent `kyria-vial-qmk` volume from `.devcontainer.json`. It survives
container recreation.

The devcontainer CLI is optional. No USB device is passed into the container,
and this setup does not dump, erase, or flash either controller.
