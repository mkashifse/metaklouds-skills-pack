#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/install.sh codex|claude [--dest /absolute/path] [--force]

Options:
  --dest PATH  Install into an explicit skills directory.
  --force      Replace existing skills after moving them to timestamped backups.
  -h, --help   Show this help.
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
        echo "Error: --dest requires a path." >&2
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
    if [[ -z "$destination" ]]; then
      destination="${CODEX_HOME:-$HOME/.codex}/skills"
    fi
    ;;
  claude)
    if [[ -z "$destination" ]]; then
      destination="${CLAUDE_HOME:-$HOME/.claude}/skills"
    fi
    ;;
  *)
    echo "Error: target must be 'codex' or 'claude'." >&2
    usage >&2
    exit 2
    ;;
esac

if [[ "$destination" != /* ]]; then
  echo "Error: destination must be an absolute path: $destination" >&2
  exit 2
fi

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "$script_directory/.." && pwd)"
temporary_root="$(mktemp -d)"
trap 'rm -rf "$temporary_root"' EXIT

mkdir -p "$destination"

install_directory() {
  local source_directory="$1"
  local skill_name="$2"
  local target_directory="$destination/$skill_name"

  if [[ ! -f "$source_directory/SKILL.md" ]]; then
    echo "Error: $source_directory is not a skill directory." >&2
    exit 1
  fi

  if [[ -e "$target_directory" ]]; then
    if [[ "$force" != "true" ]]; then
      echo "Skipping $skill_name (already installed)."
      return
    fi

    local backup_directory
    backup_directory="${target_directory}.backup-$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$target_directory" "$backup_directory"
    echo "Backed up $skill_name to $backup_directory"
  fi

  mkdir -p "$target_directory"
  cp -R "$source_directory/." "$target_directory/"
  echo "Installed $skill_name"
}

fetch_and_install() {
  local repository_url="$1"
  local revision="$2"
  local source_path="$3"
  local skill_name="$4"
  local checkout_directory="$temporary_root/$skill_name"

  if [[ -e "$destination/$skill_name" && "$force" != "true" ]]; then
    echo "Skipping $skill_name (already installed)."
    return
  fi

  git init -q "$checkout_directory"
  git -C "$checkout_directory" remote add origin "$repository_url"
  git -C "$checkout_directory" sparse-checkout init --cone
  git -C "$checkout_directory" sparse-checkout set "$source_path"
  git -C "$checkout_directory" fetch -q --depth 1 origin "$revision"
  git -C "$checkout_directory" checkout -q --detach FETCH_HEAD

  install_directory "$checkout_directory/$source_path" "$skill_name"
}

echo "Installing Metaklouds Skills Pack for $target into $destination"

install_directory "$repository_root/skills/meta-grill-team" "meta-grill-team"
install_directory "$repository_root/skills/vertical-slice-team" "vertical-slice-team"
install_directory "$repository_root/skills/dev-team" "dev-team"
install_directory "$repository_root/skills/change-management" "change-management"
install_directory "$repository_root/skills/meta-brand-guideline" "meta-brand-guideline"

fetch_and_install \
  "https://github.com/mattpocock/skills.git" \
  "2ab958093e83e0ec752e6c1c5932da465bf23e0c" \
  "skills/engineering/prototype" \
  "prototype"

fetch_and_install \
  "https://github.com/vercel-labs/agent-skills.git" \
  "7c180d9044c9ae2b442b567aad4e42a28dd5ed62" \
  "skills/react-best-practices" \
  "vercel-react-best-practices"

fetch_and_install \
  "https://github.com/fastapi/fastapi.git" \
  "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f" \
  "fastapi/.agents/skills/fastapi" \
  "fastapi"

fetch_and_install \
  "https://github.com/supabase/agent-skills.git" \
  "1207767388a0ffb55f21fb4e6988fee96942431d" \
  "skills/supabase" \
  "supabase"

fetch_and_install \
  "https://github.com/supabase/agent-skills.git" \
  "1207767388a0ffb55f21fb4e6988fee96942431d" \
  "skills/supabase-postgres-best-practices" \
  "supabase-postgres-best-practices"

echo
echo "Installed the complete skills pack."
if [[ "$target" == "codex" ]]; then
  echo "Start a new Codex task to refresh the skill catalog."
else
  echo "Restart Claude Code to refresh the skill catalog."
fi
