#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/install.sh codex|claude [--dest /absolute/path] [--force] [--only NAME]

Options:
  --dest PATH  Install into an explicit skills directory.
  --force      Replace existing skills after moving them to timestamped backups.
  --only NAME  Install only this skill. Repeat to select multiple skills.
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
only_skills=()
only_count=0

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
    --only)
      if [[ $# -lt 2 ]]; then
        echo "Error: --only requires a skill name." >&2
        exit 2
      fi
      only_skills+=("$2")
      only_count=$((only_count + 1))
      shift 2
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

if [[ "$only_count" -gt 0 ]]; then
  for selected_skill in "${only_skills[@]}"; do
    case "$selected_skill" in
      meta-pds|rapid-prototyping|slice-planning|slice-development|slice-qa|continuous-delivery-manager|delivery-monitoring-dashboard|meta-grill-team|vertical-slice-team|dev-team|change-management|prototype|vercel-react-best-practices|fastapi|supabase|supabase-postgres-best-practices)
        ;;
      *)
        echo "Error: unknown skill for --only: $selected_skill" >&2
        exit 2
        ;;
    esac
  done
fi

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "$script_directory/.." && pwd)"
temporary_root="$(mktemp -d)"
trap 'rm -rf "$temporary_root"' EXIT

mkdir -p "$destination"

should_install() {
  local skill_name="$1"
  local selected_skill

  if [[ "$only_count" -eq 0 ]]; then
    return 0
  fi

  for selected_skill in "${only_skills[@]}"; do
    if [[ "$selected_skill" == "$skill_name" ]]; then
      return 0
    fi
  done

  return 1
}

verify_meta_pds_dashboard() {
  local skill_directory="$1"
  local required_file
  local required_files=(
    scripts/serve_dashboard.py
    assets/dashboard/index.html
    assets/dashboard/styles.css
    assets/dashboard/app.js
  )

  for required_file in "${required_files[@]}"; do
    if [[ ! -f "$skill_directory/$required_file" ]]; then
      echo "Error: Meta PDS dashboard file is missing: $required_file" >&2
      exit 1
    fi
  done
}

install_directory() {
  local source_directory="$1"
  local skill_name="$2"
  local target_directory="$destination/$skill_name"

  if ! should_install "$skill_name"; then
    return
  fi

  if [[ ! -f "$source_directory/SKILL.md" ]]; then
    echo "Error: $source_directory is not a skill directory." >&2
    exit 1
  fi

  if [[ -e "$target_directory" ]]; then
    if [[ "$force" != "true" ]]; then
      if [[ "$skill_name" == "meta-pds" ]]; then
        verify_meta_pds_dashboard "$target_directory"
      fi
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
  if [[ "$skill_name" == "meta-pds" ]]; then
    verify_meta_pds_dashboard "$target_directory"
  fi
  echo "Installed $skill_name"
}

fetch_and_install() {
  local repository_url="$1"
  local revision="$2"
  local source_path="$3"
  local skill_name="$4"
  local checkout_directory="$temporary_root/$skill_name"

  if ! should_install "$skill_name"; then
    return
  fi

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

install_directory "$repository_root/meta-pds/skills/meta-pds" "meta-pds"
install_directory "$repository_root/meta-pds/skills/rapid-prototyping" "rapid-prototyping"
install_directory "$repository_root/meta-pds/skills/slice-planning" "slice-planning"
install_directory "$repository_root/meta-pds/skills/slice-development" "slice-development"
install_directory "$repository_root/meta-pds/skills/slice-qa" "slice-qa"
install_directory "$repository_root/skills/continuous-delivery-manager" "continuous-delivery-manager"
install_directory "$repository_root/skills/delivery-monitoring-dashboard" "delivery-monitoring-dashboard"
install_directory "$repository_root/skills/meta-grill-team" "meta-grill-team"
install_directory "$repository_root/skills/vertical-slice-team" "vertical-slice-team"
install_directory "$repository_root/skills/dev-team" "dev-team"
install_directory "$repository_root/skills/change-management" "change-management"

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
if [[ "$only_count" -eq 0 ]]; then
  echo "Installed the complete skills pack."
else
  echo "Installed selected skills: ${only_skills[*]}"
fi
if [[ "$target" == "codex" ]]; then
  echo "Start a new Codex task to refresh the skill catalog."
else
  echo "Restart Claude Code to refresh the skill catalog."
fi
