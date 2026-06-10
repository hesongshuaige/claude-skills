#!/usr/bin/env bash
# ldyq installer/upgrader.
# Supports Claude Code, Codex, OpenClaw, Hermes, and shared Agents skill dirs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="ldyq"
VERSION="1.1.0"

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
  --all       Install or upgrade ldyq in all existing platform skill dirs. Default.
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
echo "  ldyq installer/upgrader"
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
    echo "$platform: existing ldyq found; upgrading $target"
    rm -rf "$target"
  fi

  cp -R "$SCRIPT_DIR" "$target"
  rm -rf "$target/.git" "$target/__pycache__" "$target/install.sh.bak" 2>/dev/null || true

  INSTALLED+=("$platform -> $target")
  echo "$platform: installed $target"
done

echo ""
echo "Installed:"
if [ ${#INSTALLED[@]} -eq 0 ]; then
  echo "  none"
else
  for item in "${INSTALLED[@]}"; do
    echo "  - $item"
  done
fi

echo ""
echo "Skipped:"
if [ ${#SKIPPED[@]} -eq 0 ]; then
  echo "  none"
else
  for item in "${SKIPPED[@]}"; do
    echo "  - $item"
  done
fi

echo ""
echo "Usage examples:"
echo "  用 ldyq 写一份董事长向上争取支持的专报"
echo "  按 ldyq 审一下这份董事长汇报材料"
echo "  用 ldyq 做董事长交办事项推进方案"
