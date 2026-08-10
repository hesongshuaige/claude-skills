#!/usr/bin/env bash
# Hermes Agent Builder installer.
# Supports Claude Code, Codex, OpenClaw, Hermes, and the shared Agents directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="hermes-agent-builder"
VERSION="1.0.0"

usage() {
  cat <<'EOF'
Usage: bash install.sh [--all|--claude|--codex|--openclaw|--hermes|--agents]

The default is --all. Existing installations are moved to a timestamped backup
before the new copy is activated. Set HERMES_SKILLS_DIR to target a profile-
specific Hermes skills directory when the global Hermes directory is not used.
EOF
}

case "${1:---all}" in
  --all) TARGETS=(claude codex openclaw hermes agents) ;;
  --claude|--codex|--openclaw|--hermes|--agents) TARGETS=("${1#--}") ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 1 ;;
esac

declare -A DEFAULT_DIRS=(
  [claude]="$HOME/.claude/skills"
  [codex]="$HOME/.codex/skills"
  [openclaw]="$HOME/.openclaw/skills"
  [hermes]="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"
  [agents]="$HOME/.agents/skills"
)

stamp="$(date +%Y%m%d%H%M%S)"
for platform in "${TARGETS[@]}"; do
  target_dir="${DEFAULT_DIRS[$platform]}"
  target="$target_dir/$SKILL_NAME"
  mkdir -p "$target_dir"
  if [ -e "$target" ] || [ -L "$target" ]; then
    backup="$target.bak.$stamp"
    mv "$target" "$backup"
    echo "$platform: backed up existing skill to $backup"
  fi
  stage="$(mktemp -d "${target_dir}/.${SKILL_NAME}.stage.XXXXXX")"
  cp -R "$SCRIPT_DIR/." "$stage/"
  rm -rf "$stage/.git" "$stage/__pycache__"
  mv "$stage" "$target"
  echo "$platform: installed $target"
done

echo "Hermes Agent Builder $VERSION installed."
