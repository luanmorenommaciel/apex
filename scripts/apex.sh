#!/usr/bin/env bash
# macOS entry point for the Apex package. The package orchestration remains in
# apex.ps1 so Windows and macOS run the same bootstrap and safety checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-help}"
shift || true
DOCKER_APP_BIN="/Applications/Docker.app/Contents/Resources/bin"

add_docker_app_bin() {
  if [[ -x "$DOCKER_APP_BIN/docker" ]]; then
    export PATH="$DOCKER_APP_BIN:$PATH"
  fi
}

install_docker_desktop() {
  local dmg mount_dir

  if [[ -x "$DOCKER_APP_BIN/docker" ]]; then
    return
  fi

  # Homebrew's cask runs privileged post-install symlinks. Fetching its
  # verified DMG and copying the app bundle avoids those system-wide links.
  brew fetch --cask docker-desktop
  dmg="$(brew --cache --cask docker-desktop)"
  mount_dir="$(mktemp -d /private/tmp/apex-docker.XXXXXX)"
  hdiutil attach "$dmg" -nobrowse -readonly -mountpoint "$mount_dir"
  ditto "$mount_dir/Docker.app" /Applications/Docker.app
  hdiutil detach "$mount_dir"
  rmdir "$mount_dir"
}

usage() {
  cat <<'EOF'
Apex macOS package entry point

  ./scripts/apex.sh install     Install local prerequisites with Homebrew
  ./scripts/apex.sh bootstrap   Build and start the package
  ./scripts/apex.sh doctor|smoke|e2e|tail-outlier|pilot-clean|status|down

`install` installs PowerShell, uv, and Docker Desktop when absent. Start
Docker Desktop and wait until its engine is running before `bootstrap`.
EOF
}

require_macos() {
  if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "scripts/apex.sh install is supported only on macOS; use scripts/apex.ps1 on Windows." >&2
    exit 2
  fi
}

install_prerequisites() {
  require_macos
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required. Install it from https://brew.sh, then rerun this command." >&2
    exit 2
  fi

  if ! command -v pwsh >/dev/null 2>&1; then
    brew install powershell
  fi
  if ! command -v uv >/dev/null 2>&1; then
    brew install uv
  fi
  uv python install 3.11
  if ! command -v docker >/dev/null 2>&1; then
    install_docker_desktop
  fi

  cat <<'EOF'
APEX_MAC_INSTALL=complete
Start Docker Desktop, wait until `docker info` succeeds, then run:
  ./scripts/apex.sh bootstrap
EOF
}

if [[ "$ACTION" == "install" ]]; then
  install_prerequisites
  exit 0
fi

case "$ACTION" in
  bootstrap|doctor|smoke|e2e|tail-outlier|pilot-clean|status|down|help)
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

require_macos
add_docker_app_bin
if ! command -v pwsh >/dev/null 2>&1; then
  echo "PowerShell 7 is required. Run ./scripts/apex.sh install first." >&2
  exit 2
fi

exec pwsh -NoProfile -ExecutionPolicy Bypass -File "$ROOT/scripts/apex.ps1" "$ACTION" "$@"
