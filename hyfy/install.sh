#!/bin/bash
# 发言稿工坊（hyfy）一键安装脚本
# 支持：Claude Code / Codex CLI / OpenClaw / Hermes / Agents
# 用法：bash install.sh [--all|--claude|--codex|--openclaw|--hermes|--agents]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="hyfy"
VERSION="1.0.1"

# 平台定义
declare -A PLATFORMS=(
  ["claude"]="$HOME/.claude/skills"
  ["codex"]="$HOME/.codex/skills"
  ["openclaw"]="$HOME/.openclaw/skills"
  ["hermes"]="$HOME/.hermes/skills"
  ["agents"]="$HOME/.agents/skills"
)

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "======================================"
echo "  发言稿工坊（$SKILL_NAME）安装程序"
echo "  版本: $VERSION"
echo "======================================"
echo ""

# 解析参数
INSTALL_TARGETS=()
case "${1:-}" in
  --all|"")
    INSTALL_TARGETS=("claude" "codex" "openclaw" "hermes" "agents")
    ;;
  --claude|--codex|--openclaw|--hermes|--agents)
    INSTALL_TARGETS=("${1#--}")
    ;;
  -h|--help)
    echo "用法: bash install.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --all       安装到所有平台（默认）"
    echo "  --claude    仅安装到 Claude Code"
    echo "  --codex     仅安装到 Codex CLI"
    echo "  --openclaw  仅安装到 OpenClaw"
    echo "  --hermes    仅安装到 Hermes"
    echo "  --agents    仅安装到通用 agents 目录"
    echo "  -h, --help  显示帮助"
    exit 0
    ;;
  *)
    echo -e "${RED}✗ 未知选项: $1${NC}"
    echo "  运行 'bash install.sh --help' 查看帮助"
    exit 1
    ;;
esac

# 检测并安装
INSTALLED=()
SKIPPED=()

for platform in "${INSTALL_TARGETS[@]}"; do
  target_dir="${PLATFORMS[$platform]}"
  target="$target_dir/$SKILL_NAME"
  
  # 父目录是否存在 = 该平台是否可能存在
  if [ ! -d "$target_dir" ]; then
    # 父目录不存在，跳过
    SKIPPED+=("$platform (目录不存在: $target_dir)")
    continue
  fi
  
  # 已存在则备份提示
  if [ -d "$target" ]; then
    echo -e "${YELLOW}⚠ $platform: 检测到已存在的 $SKILL_NAME，将更新${NC}"
    rm -rf "$target"
  fi
  
  # 复制
  cp -r "$SCRIPT_DIR" "$target"
  # 清理不必要的文件
  rm -rf "$target/__pycache__" "$target/.git" "$target/install.sh.bak" 2>/dev/null || true
  
  INSTALLED+=("$platform → $target")
  echo -e "${GREEN}✓ $platform: 已安装到 $target${NC}"
done

# Python 依赖检测（hyfy 联动 pb 时需要 python-docx）
echo ""
echo "─── Python 依赖检测 ───"
PYTHON_OK=false
if command -v python3 &> /dev/null; then
  if python3 -c "import docx" 2>/dev/null; then
    echo -e "${GREEN}✓ python-docx 已安装（hyfy 联动 pb 时需要）${NC}"
    PYTHON_OK=true
  else
    echo -e "${YELLOW}⚠ python-docx 未安装（hyfy 联动 pb 时需要）${NC}"
    if command -v pip3 &> /dev/null; then
      read -p "  现在安装 python-docx 吗? [Y/n] " yn
      yn=${yn:-Y}
      if [[ "$yn" =~ ^[Yy]$ ]]; then
        pip3 install -q --user python-docx 2>/dev/null || \
        pip3 install -q python-docx 2>/dev/null || \
        echo -e "${RED}✗ 安装失败，请手动: pip3 install python-docx${NC}"
        if python3 -c "import docx" 2>/dev/null; then
          echo -e "${GREEN}✓ python-docx 已安装${NC}"
          PYTHON_OK=true
        fi
      fi
    else
      echo -e "${YELLOW}  请手动安装: pip3 install python-docx${NC}"
    fi
  fi
else
  echo -e "${YELLOW}⚠ 未检测到 python3，hyfy 仍可使用（联动 pb 时需 python3 + python-docx）${NC}"
fi

# 安装摘要
echo ""
echo "======================================"
echo "  安装摘要"
echo "======================================"
echo ""
if [ ${#INSTALLED[@]} -gt 0 ]; then
  echo -e "${GREEN}已安装到 ${#INSTALLED[@]} 个平台:${NC}"
  for i in "${INSTALLED[@]}"; do
    echo "  ✓ $i"
  done
fi
if [ ${#SKIPPED[@]} -gt 0 ]; then
  echo ""
  echo -e "${YELLOW}已跳过 ${#SKIPPED[@]} 个平台（目录不存在）:${NC}"
  for i in "${SKIPPED[@]}"; do
    echo "  - $i"
  done
  echo ""
  echo "  提示: 跳过的平台说明未安装该 agent 工具。"
  echo "  安装相应工具后再次运行本脚本即可。"
fi
echo ""
echo "======================================"
echo "  使用方法"
echo "======================================"
echo ""
echo "  对 AI Agent 说："
echo "    \"用 hyfy 帮我写个下周去拜访 XX 集团的发言稿，5 分钟，董事长用\""
echo ""
echo "  或者直接触发："
echo "    \"hyfy：写个 XX 致辞\""
echo ""
echo "  写完内容后建议联动 pb 排版："
echo "    \"联动 pb 排版\" → 上传飞书云空间 → 返回下载链接"
echo ""
