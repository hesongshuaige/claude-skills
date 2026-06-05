#!/usr/bin/env bash
# AISC installer/upgrader.
# Supports Claude Code, Codex, OpenClaw, Hermes, and shared Agents skill dirs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="aisc"
VERSION="2.0.0"

declare -A PLATFORMS=(
  ["claude"]="$HOME/.claude/skills"
  ["codex"]="$HOME/.codex/skills"
  ["openclaw"]="$HOME/.openclaw/skills"
  ["hermes"]="$HOME/.hermes/skills"
  ["agents"]="$HOME/.agents/skills"
)

usage() {
  cat <<'EOF'
Usage: bash install.sh [--all|--claude|--codex|--openclaw|--hermes|--agents]

Options:
  --all       Install or upgrade AISC in all existing platform skill dirs. Default.
  --claude    Install or upgrade only Claude Code.
  --codex     Install or upgrade only Codex.
  --openclaw  Install or upgrade only OpenClaw.
  --hermes    Install or upgrade only Hermes.
  --agents    Install or upgrade only the shared Agents dir.
  -h, --help  Show this help.
EOF
}

case "${1:---all}" in
  --all)
    TARGETS=("claude" "codex" "openclaw" "hermes" "agents")
    ;;
  --claude|--codex|--openclaw|--hermes|--agents)
    TARGETS=("${1#--}")
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    usage
    exit 1
    ;;
esac

echo "======================================"
echo "  AISC installer/upgrader"
echo "  Version: $VERSION"
echo "======================================"

INSTALLED=()
SKIPPED=()

for platform in "${TARGETS[@]}"; do
  target_dir="${PLATFORMS[$platform]}"
  target="$target_dir/$SKILL_NAME"

  if [ ! -d "$target_dir" ]; then
    SKIPPED+=("$platform: missing $target_dir")
    continue
  fi

  if [ -d "$target" ]; then
    echo "$platform: existing AISC found; upgrading $target"
    rm -rf "$target"
  else
    echo "$platform: installing to $target"
  fi

  mkdir -p "$target_dir"
  cp -R "$SCRIPT_DIR" "$target"
  rm -rf "$target/.git" "$target/__pycache__" "$target/scripts/__pycache__" 2>/dev/null || true
  INSTALLED+=("$platform: $target")
done

echo ""
echo "Install summary"
echo "---------------"
if [ "${#INSTALLED[@]}" -gt 0 ]; then
  echo "Installed/upgraded:"
  for item in "${INSTALLED[@]}"; do
    echo "  - $item"
  done
else
  echo "No platform skill dirs were found."
fi

if [ "${#SKIPPED[@]}" -gt 0 ]; then
  echo ""
  echo "Skipped:"
  for item in "${SKIPPED[@]}"; do
    echo "  - $item"
  done
fi

echo ""
echo "Usage examples:"
echo "  用aisc处理这篇文章：[链接或正文]"
echo "  aisc一下这段录音稿，并沉淀到飞书"
echo "  Use AISC to make a quality-gated learning card from this report."
