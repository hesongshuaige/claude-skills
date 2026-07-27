#!/usr/bin/env bash
# skillyes 一键安装脚本（5 平台复制式）
# 用法：bash install.sh [--all|--claude|--codex|--openclaw|--hermes|--agents]
#   默认装到所有已检测平台。示例：bash install.sh --claude
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # skillyes/ 目录（scripts/ 的上一级）
SKILL_NAME="skillyes"

declare -A PLATFORMS=(
  ["claude"]="$HOME/.claude/skills"
  ["codex"]="$HOME/.codex/skills"
  ["openclaw"]="$HOME/.openclaw/skills"
  ["hermes"]="$HOME/.hermes/skills"
  ["agents"]="$HOME/.agents/skills"
)

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --all) TARGETS=("claude" "codex" "openclaw" "hermes" "agents"); shift ;;
    --claude|--codex|--openclaw|--hermes|--agents) TARGETS+=("${1#--}"); shift ;;
    -h|--help)
      cat <<EOF
用法: bash install.sh [选项]

平台（选一或 --all，默认 --all）:
  --all          所有平台（默认）
  --claude       Claude Code
  --codex        Codex CLI
  --openclaw     OpenClaw
  --hermes       Hermes
  --agents       通用 agents 目录

示例:
  bash install.sh                # 装到所有平台
  bash install.sh --claude       # 仅 Claude Code
  bash install.sh --codex --hermes   # Codex + Hermes
EOF
      exit 0 ;;
    *) echo "✗ 未知选项: $1（--help 查看帮助）"; exit 1 ;;
  esac
done
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=("claude" "codex" "openclaw" "hermes" "agents")

SRC="$SCRIPT_DIR"
if [ ! -f "$SRC/SKILL.md" ] || [ ! -f "$SRC/REFERENCE.md" ] || [ ! -d "$SRC/scripts" ]; then
  echo "✗ 目录不完整（缺 SKILL.md/REFERENCE.md/scripts）：$SRC"; exit 1
fi

echo "======================================"
echo "  skillyes 安装（提示词出库查找 + 学习教练）"
echo "======================================"
echo ""

INSTALLED=(); SKIPPED=()
for p in "${TARGETS[@]}"; do
  td="${PLATFORMS[$p]}"
  if [ ! -d "$td" ]; then SKIPPED+=("$p (目录不存在，跳过)"); continue; fi
  if [ -d "$td/$SKILL_NAME" ]; then
    echo -e "${YELLOW}⚠ $p: 已存在，将更新${NC}"
    rm -rf "$td/$SKILL_NAME"
  fi
  mkdir -p "$td/$SKILL_NAME"
  cp "$SRC/SKILL.md" "$td/$SKILL_NAME/"
  cp "$SRC/REFERENCE.md" "$td/$SKILL_NAME/"
  cp -r "$SRC/scripts" "$td/$SKILL_NAME/"
  INSTALLED+=("$p")
  echo -e "${GREEN}✓ $p → $td/$SKILL_NAME${NC}"
done

echo ""
echo "完成。"
[ ${#INSTALLED[@]} -gt 0 ] && echo "已安装: ${INSTALLED[*]}"
[ ${#SKIPPED[@]} -gt 0 ] && echo "已跳过: ${SKIPPED[*]}"
echo ""
echo "下一步（必做，否则 fetch 跑不通）："
echo "  1. 配置飞书库（二选一）："
echo "     A) 环境变量（写进 ~/.bashrc）："
echo "          export SKILLYES_SPACE_ID=<你的飞书 space_id>"
echo "          export SKILLYES_INDEX_TOKEN=<索引页 file_token>"
echo "     B) 配置文件 ~/.config/skillyes.conf（两行 KEY=VALUE）"
echo "  2. 装 lark-cli 并 lark-cli auth login（user 身份）"
echo "  3. 在对应客户端说 '帮我找个提示词' 或 '/skillyes' + 贴问题"
echo ""
echo "⚠ Hermes / OpenClaw 若不自动识别 skills 目录，参考 README 的 AGENTS.md 注入法。"
