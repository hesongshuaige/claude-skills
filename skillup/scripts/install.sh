#!/usr/bin/env bash
# skillup 一键安装脚本（多版本可选）
# 用法：bash install.sh [--version v1|v2|v3] [--all|--claude|--codex|--openclaw|--hermes|--agents]
#   默认装 v3（最新）。示例：bash install.sh --version v1 --claude
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # skillup/ 目录（scripts/ 的上一级）
SKILL_NAME="skillup"

declare -A PLATFORMS=(
  ["claude"]="$HOME/.claude/skills"
  ["codex"]="$HOME/.codex/skills"
  ["openclaw"]="$HOME/.openclaw/skills"
  ["hermes"]="$HOME/.hermes/skills"
  ["agents"]="$HOME/.agents/skills"
)

declare -A VERSION_DIR=(
  ["v3"]="$SCRIPT_DIR"
  ["v2"]="$SCRIPT_DIR/archive/v2-fenxing"
  ["v1"]="$SCRIPT_DIR/archive/v1-basic"
)

declare -A VERSION_DESC=(
  ["v3"]="最新：身份+writing-skills方法论+硬伤单一来源（4池）"
  ["v2"]="分型版：A/B分型+硬伤制（4池）"
  ["v1"]="基础版：2池7步基础流程"
)

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

VERSION="v3"
TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --v1) VERSION="v1"; shift ;;
    --v2) VERSION="v2"; shift ;;
    --v3) VERSION="v3"; shift ;;
    --all) TARGETS=("claude" "codex" "openclaw" "hermes" "agents"); shift ;;
    --claude|--codex|--openclaw|--hermes|--agents) TARGETS+=("${1#--}"); shift ;;
    -h|--help)
      cat <<EOF
用法: bash install.sh [选项]

版本（选一，默认 v3）:
  --version v3   最新：身份+writing-skills方法论+硬伤单一来源（4池）
  --version v2   分型版：A/B分型+硬伤制（4池）
  --version v1   基础版：2池7步基础流程
  （简写: --v1 / --v2 / --v3）

平台（选一或 --all，默认 --all）:
  --all          所有已检测平台（默认）
  --claude       仅 Claude Code
  --codex        仅 Codex CLI
  --openclaw     仅 OpenClaw
  --hermes       仅 Hermes
  --agents       仅通用 agents 目录

示例:
  bash install.sh                          # 装最新 v3 到所有平台
  bash install.sh --version v1 --claude    # 装基础版 v1 到 Claude Code
  bash install.sh --v2 --codex             # 装分型版 v2 到 Codex
EOF
      exit 0 ;;
    *) echo "✗ 未知选项: $1（--help 查看帮助）"; exit 1 ;;
  esac
done
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=("claude" "codex" "openclaw" "hermes" "agents")

# 定位版本源目录
SRC="${VERSION_DIR[$VERSION]:-}"
if [ -z "$SRC" ] || [ ! -d "$SRC" ]; then
  echo "✗ 未知版本或目录不存在: $VERSION（可选 v1/v2/v3）"; exit 1
fi
if [ ! -f "$SRC/SKILL.md" ] || [ ! -f "$SRC/REFERENCE.md" ] || [ ! -d "$SRC/scripts" ]; then
  echo "✗ 版本 $VERSION 目录不完整（缺 SKILL.md/REFERENCE.md/scripts）：$SRC"; exit 1
fi

echo "======================================"
echo "  skillup 安装  版本: $VERSION"
echo "  ${VERSION_DESC[$VERSION]}"
echo "======================================"
echo ""

INSTALLED=(); SKIPPED=()
for p in "${TARGETS[@]}"; do
  td="${PLATFORMS[$p]}"
  if [ ! -d "$td" ]; then SKIPPED+=("$p (目录不存在)"); continue; fi
  if [ -d "$td/$SKILL_NAME" ]; then
    echo -e "${YELLOW}⚠ $p: 已存在，将更新${NC}"
    rm -rf "$td/$SKILL_NAME"
  fi
  mkdir -p "$td/$SKILL_NAME"
  cp "$SRC/SKILL.md" "$td/$SKILL_NAME/"
  cp "$SRC/REFERENCE.md" "$td/$SKILL_NAME/"
  cp -r "$SRC/scripts" "$td/$SKILL_NAME/"
  INSTALLED+=("$p")
  echo -e "${GREEN}✓ $p → $td/$SKILL_NAME（$VERSION）${NC}"
done

echo ""
echo "完成。"
[ ${#INSTALLED[@]} -gt 0 ] && echo "已安装($VERSION): ${INSTALLED[*]}"
[ ${#SKIPPED[@]} -gt 0 ] && echo "已跳过: ${SKIPPED[*]}"
echo ""
echo "下一步（必做，否则上传步骤跑不通）："
echo "  1. 配置飞书库: 在 ~/.bashrc 加"
echo "       export SKILLUP_SPACE_ID=<飞书 space_id>"
echo "       export SKILLUP_INDEX_TOKEN=<索引页 file_token>"
echo "     或写 ~/.config/skillup.conf（两行 KEY=VALUE）"
echo "  2. 装 lark-cli 并 lark-cli auth login（user 身份）"
echo "  3. 配 MiniMax key: export MINIMAX_API_KEY=... 或 ~/.secrets/mm.env"
echo "  4. 在对应客户端说 'skillup' 或 '/skillup' 触发"
