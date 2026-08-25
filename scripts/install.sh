#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/install.sh codex|claude [--dest /absolute/path] [--force] [--only NAME]

Options:
  --dest PATH  Install into an explicit skills directory.
  --force      Replace existing skills after moving them to timestamped backups.
  --only NAME  Install selected skills. Selecting solo-founder installs its complete profile.
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
install_complete_profile="false"
profile_skills=(
  solo-founder
  vercel-react-best-practices
  frontend-design
  vercel-composition-patterns
  fastapi
  nodejs-backend-patterns
  python-testing-patterns
  vitest
  playwright-best-practices
  supabase
  supabase-postgres-best-practices
)
legacy_skills=(
  meta-pds
  rapid-prototyping
  slice-planning
  slice-development
  slice-qa
  continuous-delivery-manager
  delivery-monitoring-dashboard
  meta-grill-team
  vertical-slice-team
  dev-team
  change-management
)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      [[ $# -ge 2 ]] || { echo "Error: --dest requires a path." >&2; exit 2; }
      destination="$2"
      shift 2
      ;;
    --force)
      force="true"
      shift
      ;;
    --only)
      [[ $# -ge 2 ]] || { echo "Error: --only requires a skill name." >&2; exit 2; }
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
    destination="${destination:-${CODEX_HOME:-$HOME/.codex}/skills}"
    ;;
  claude)
    destination="${destination:-${CLAUDE_HOME:-$HOME/.claude}/skills}"
    ;;
  *)
    echo "Error: target must be 'codex' or 'claude'." >&2
    exit 2
    ;;
esac

[[ "$destination" == /* ]] || { echo "Error: destination must be absolute: $destination" >&2; exit 2; }

if [[ "$only_count" -gt 0 ]]; then
  for selected_skill in "${only_skills[@]}"; do
    case "$selected_skill" in
      solo-founder)
        install_complete_profile="true"
        ;;
      vercel-react-best-practices|frontend-design|vercel-composition-patterns|fastapi|nodejs-backend-patterns|python-testing-patterns|vitest|playwright-best-practices|supabase|supabase-postgres-best-practices)
        ;;
      *)
        echo "Error: unknown skill for --only: $selected_skill" >&2
        exit 2
        ;;
    esac
  done
else
  install_complete_profile="true"
fi

if [[ "$install_complete_profile" == "true" ]]; then
  only_skills=("${profile_skills[@]}")
  only_count="${#only_skills[@]}"
fi

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "$script_directory/.." && pwd)"
temporary_root="$(mktemp -d)"
trap 'rm -rf "$temporary_root"' EXIT
backup_root="$(dirname "$destination")/metaklouds-skills-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$destination"

should_install() {
  local skill_name="$1"
  local selected
  for selected in "${only_skills[@]}"; do
    [[ "$selected" == "$skill_name" ]] && return 0
  done
  return 1
}

verify_solo_founder_bundle() {
  local skill_directory="$1"
  local required
  local required_files=(
    agents/openai.yaml
    scripts/restore_context.py
    scripts/create_handoff.py
    scripts/update_ledger.py
    scripts/validate_artifacts.py
    scripts/serve_dashboard.py
    references/modes-and-layers.md
    references/truth-and-product-ledger.md
    references/work-classification.md
    references/handoff-contract.md
    references/repository-structure.md
    references/production-prototyping.md
    references/fat-slice-planning.md
    references/implementation-and-quality.md
    references/dashboard-contract.md
    assets/canonical-truth-template.yaml
    assets/product-ledger-template.yaml
    assets/handoff-template.md
    assets/research-template.md
    assets/fat-slice-template.md
    assets/dashboard/index.html
    assets/dashboard/styles.css
    assets/dashboard/demo-data.js
    assets/dashboard/app.js
  )
  for required in "${required_files[@]}"; do
    [[ -f "$skill_directory/$required" ]] || { echo "Error: Solo Founder bundled file is missing: $required" >&2; exit 1; }
  done
}

move_to_backup() {
  local target_directory="$1"
  local skill_name="$2"
  mkdir -p "$backup_root"
  mv "$target_directory" "$backup_root/$skill_name"
  echo "Backed up $skill_name to $backup_root/$skill_name"
}

retire_legacy_skill() {
  local skill_name="$1"
  local target_directory="$destination/$skill_name"
  if [[ -e "$target_directory" ]]; then
    move_to_backup "$target_directory" "$skill_name"
    echo "Retired legacy skill $skill_name"
  fi
}

install_directory() {
  local source_directory="$1"
  local skill_name="$2"
  local target_directory="$destination/$skill_name"
  should_install "$skill_name" || return 0
  [[ -f "$source_directory/SKILL.md" ]] || { echo "Error: $source_directory is not a skill directory." >&2; exit 1; }
  if [[ -e "$target_directory" ]]; then
    if [[ "$force" != "true" ]]; then
      [[ "$skill_name" != "solo-founder" ]] || verify_solo_founder_bundle "$target_directory"
      echo "Skipping $skill_name (already installed)."
      return 0
    fi
    move_to_backup "$target_directory" "$skill_name"
  fi
  mkdir -p "$target_directory"
  cp -R "$source_directory/." "$target_directory/"
  [[ "$skill_name" != "solo-founder" ]] || verify_solo_founder_bundle "$target_directory"
  echo "Installed $skill_name"
}

fetch_and_install() {
  local repository_url="$1"
  local revision="$2"
  local source_path="$3"
  local skill_name="$4"
  local checkout_directory="$temporary_root/$skill_name"
  should_install "$skill_name" || return 0
  if [[ -e "$destination/$skill_name" && "$force" != "true" ]]; then
    echo "Skipping $skill_name (already installed)."
    return 0
  fi
  git init -q "$checkout_directory"
  git -C "$checkout_directory" remote add origin "$repository_url"
  git -C "$checkout_directory" sparse-checkout init --cone
  git -C "$checkout_directory" sparse-checkout set "$source_path"
  git -C "$checkout_directory" fetch -q --depth 1 origin "$revision"
  git -C "$checkout_directory" checkout -q --detach FETCH_HEAD
  install_directory "$checkout_directory/$source_path" "$skill_name"
}

echo "Installing Solo Founder Skills Pack for $target into $destination"

if [[ "$install_complete_profile" == "true" ]]; then
  for legacy_skill in "${legacy_skills[@]}"; do
    retire_legacy_skill "$legacy_skill"
  done
fi

install_directory "$repository_root/solo-founder/skills/solo-founder" "solo-founder"

fetch_and_install "https://github.com/vercel-labs/agent-skills.git" "7c180d9044c9ae2b442b567aad4e42a28dd5ed62" "skills/react-best-practices" "vercel-react-best-practices"
fetch_and_install "https://github.com/anthropics/skills.git" "3b3fad96af16a10759d930941b4520ba0c40edae" "skills/frontend-design" "frontend-design"
fetch_and_install "https://github.com/vercel-labs/agent-skills.git" "dd089a8c752c966dee8bf0f27cb625ba193ffd9e" "skills/composition-patterns" "vercel-composition-patterns"
fetch_and_install "https://github.com/fastapi/fastapi.git" "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f" "fastapi/.agents/skills/fastapi" "fastapi"
fetch_and_install "https://github.com/wshobson/agents.git" "367cb6a4a182cf7e9b0a17c9429f7411ddd9cf35" "plugins/javascript-typescript/skills/nodejs-backend-patterns" "nodejs-backend-patterns"
fetch_and_install "https://github.com/wshobson/agents.git" "367cb6a4a182cf7e9b0a17c9429f7411ddd9cf35" "plugins/python-development/skills/python-testing-patterns" "python-testing-patterns"
fetch_and_install "https://github.com/antfu/skills.git" "a74f281a27dadc02397bc1a174b0f2c97531b6ae" "skills/vitest" "vitest"
fetch_and_install "https://github.com/currents-dev/playwright-best-practices-skill.git" "283d5cbc5d11aac1abda058b16ad22c317d54dc0" "playwright-best-practices" "playwright-best-practices"
fetch_and_install "https://github.com/supabase/agent-skills.git" "1207767388a0ffb55f21fb4e6988fee96942431d" "skills/supabase" "supabase"
fetch_and_install "https://github.com/supabase/agent-skills.git" "1207767388a0ffb55f21fb4e6988fee96942431d" "skills/supabase-postgres-best-practices" "supabase-postgres-best-practices"

echo
if [[ "$install_complete_profile" == "true" ]]; then
  echo "Installed the complete Solo Founder profile (11 skills)."
else
  echo "Installed selected skills: ${only_skills[*]}"
fi
if [[ "$target" == "codex" ]]; then
  echo "Start a new Codex task to refresh the skill catalog, then invoke: Use \$solo-founder"
else
  echo "Restart Claude Code, then invoke: Use \$solo-founder"
fi
