#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./meta-pds/scripts/install.sh codex|claude [--dest /absolute/path] [--force]

Installs the complete Meta PDS suite. The five skills are intentionally
installed together because the functional skills inherit policy from meta-pds.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

target="$1"
shift
destination=""
force="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      if [[ $# -lt 2 ]]; then
        echo "Error: --dest requires an absolute path." >&2
        exit 2
      fi
      destination="$2"
      shift 2
      ;;
    --force)
      force="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$target" in
  codex)
    destination="${destination:-${CODEX_HOME:-$HOME/.codex}/skills}"
    ;;
  claude)
    destination="${destination:-${CLAUDE_HOME:-$HOME/.claude}/skills}"
    ;;
  *)
    echo "Error: target must be codex or claude." >&2
    exit 2
    ;;
esac

if [[ "$destination" != /* ]]; then
  echo "Error: destination must be absolute: $destination" >&2
  exit 2
fi

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
suite_root="$(cd "$script_directory/.." && pwd)"
skills=(meta-pds rapid-prototyping slice-planning slice-development slice-qa)
dashboard_files=(
  scripts/serve_dashboard.py
  assets/dashboard/index.html
  assets/dashboard/styles.css
  assets/dashboard/app.js
)

mkdir -p "$destination"

for skill in "${skills[@]}"; do
  source_directory="$suite_root/skills/$skill"
  target_directory="$destination/$skill"

  if [[ ! -f "$source_directory/SKILL.md" ]]; then
    echo "Error: missing skill source: $source_directory" >&2
    exit 1
  fi

  if [[ -e "$target_directory" ]]; then
    if [[ "$force" != "true" ]]; then
      if [[ "$skill" == "meta-pds" ]]; then
        for dashboard_file in "${dashboard_files[@]}"; do
          if [[ ! -f "$target_directory/$dashboard_file" ]]; then
            echo "Error: installed Meta PDS dashboard file is missing: $dashboard_file" >&2
            exit 1
          fi
        done
      fi
      echo "Skipping $skill (already installed)."
      continue
    fi
    backup_directory="${target_directory}.backup-$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$target_directory" "$backup_directory"
    echo "Backed up $skill to $backup_directory"
  fi

  mkdir -p "$target_directory"
  cp -R "$source_directory/." "$target_directory/"
  if [[ "$skill" == "meta-pds" ]]; then
    for dashboard_file in "${dashboard_files[@]}"; do
      if [[ ! -f "$target_directory/$dashboard_file" ]]; then
        echo "Error: Meta PDS dashboard file was not installed: $dashboard_file" >&2
        exit 1
      fi
    done
  fi
  echo "Installed $skill"
done

echo 'Meta PDS installation complete. Start a new task and invoke: Use $meta-pds'
