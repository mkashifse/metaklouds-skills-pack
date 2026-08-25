#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: ./solo-founder/scripts/install.sh codex|claude [--dest /absolute/path] [--force]" >&2
  exit 2
fi

target="$1"
shift
script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "$script_directory/../.." && pwd)"
exec "$repository_root/scripts/install.sh" "$target" "$@" --only solo-founder
