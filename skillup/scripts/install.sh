#!/usr/bin/env bash
# skillup 一键安装脚本
# 支持：Claude Code / Codex CLI / OpenClaw / Hermes / Agents
# 用法：bash install.sh [--all|--claude|--codex|--openclaw|--hermes|--agents]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # skillup/ 目录（scripts/ 的上一级）
SKILL_NAME="skillup"
VERSION="1.0.0"

declare -A PLATFORMS=(
  ["claude"]="$HOME/.claude/skills"
  ["codex"]="$HOME/.codex/skills"
  ["openclaw"]="$HOME/.openclaw/skills"
  ["hermes"]="$HOME/.hermes/skills"
  ["agents"]="$HOME/.agents/skills"
)

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "======================================"
echo "  skillup 安装程序  版本: $VERSION"
echo "======================================"
echo ""

case "${1:-}" in
  --all|"") TARGETS=("claude" "codex" "openclaw" "hermes" "agents") ;;
  --claude|--codex|--openclaw|--hermes|--agents) TARGETS=("${1#--}") ;;
  -h|--help)
    echo "用法: bash install.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --all       安装到所有已检测到的平台（默认）"
    echo "  --claude    仅 Claude Code"
    echo "  --codex     仅 Codex CLI"
    echo "  --openclaw  仅 OpenClaw"
    echo "  --hermes    仅 Hermes"
    echo "  --agents    仅通用 agents 目录"
    echo "  -h, --help  显示帮助"
    exit 0 ;;
  *) echo "✗ 未知选项: $1（运行 bash install.sh --help 查看帮助）"; exit 1 ;;
esac

INSTALLED=(); SKIPPED=()
for p in "${TARGETS[@]}"; do
  td="${PLATFORMS[$p]}"
  if [ ! -d "$td" ]; then SKIPPED+=("$p (目录不存在)"); continue; fi
  if [ -d "$td/$SKILL_NAME" ]; then
    echo -e "${YELLOW}⚠ $p: 已存在，将更新${NC}"
    rm -rf "$td/$SKILL_NAME"
  fi
  cp -r "$SCRIPT_DIR" "$td/$SKILL_NAME"
  INSTALLED+=("$p")
  echo -e "${GREEN}✓ $p → $td/$SKILL_NAME${NC}"
done

echo ""
echo "完成。"
[ ${#INSTALLED[@]} -gt 0 ] && echo "已安装: ${INSTALLED[*]}"
[ ${#SKIPPED[@]} -gt 0 ] && echo "已跳过: ${SKIPPED[*]}"
echo ""
echo "下一步（必做）："
echo "  1. 配置飞书库: 在 ~/.bashrc 加"
echo "       export SKILLUP_SPACE_ID=<飞书 space_id>"
echo "       export SKILLUP_INDEX_TOKEN=<索引页 file_token>"
echo "     或写 ~/.config/skillup.conf（见 SKILL.md）"
echo "  2. 装 lark-cli 并 lark-cli auth login（user 身份）"
echo "  3. 配 MiniMax key: export MINIMAX_API_KEY=... 或 ~/.secrets/mm.env"
echo "  4. 在对应客户端说 'skillup' 或 '/skillup' 触发"
