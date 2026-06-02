#!/bin/bash
# 投资研判技能（go / touyan-pb）一键安装脚本
# 支持：Claude Code / Codex CLI / OpenClaw / Hermes
set -e

echo "======================================"
echo "  投资研判技能（go）安装程序"
echo "======================================"
echo ""

# 1. 检测 skills 目录（兼容多平台）
SKILL_DIR=""
for candidate in \
  "$HOME/.claude/skills" \
  "$HOME/.codex/skills" \
  "$HOME/.openclaw/skills" \
  "$HOME/.hermes/skills" \
  "$HOME/.config/claude/skills"; do
  if [ -d "$candidate" ] || [ -d "$(dirname "$candidate")" ]; then
    SKILL_DIR="$candidate"
    break
  fi
done

if [ -z "$SKILL_DIR" ]; then
  echo "未检测到 skills 目录，使用默认路径 ~/.claude/skills"
  SKILL_DIR="$HOME/.claude/skills"
fi

echo "✓ Skills 目录: $SKILL_DIR"

# 2. 复制技能文件
TARGET="$SKILL_DIR/go"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -d "$TARGET" ]; then
  echo "⚠ 检测到已存在的 go 技能目录，将更新"
  rm -rf "$TARGET"
fi

cp -r "$SCRIPT_DIR" "$TARGET"
# 清理不需要的文件
rm -rf "$TARGET/__pycache__" "$TARGET/.git" "$TARGET/install.sh.bak" 2>/dev/null || true
echo "✓ 技能文件已复制到 $TARGET"

# 3. 安装 Python 依赖
echo ""
echo "正在安装 Python 依赖..."
if command -v pip3 &> /dev/null; then
  pip3 install -q -r "$TARGET/scripts/requirements.txt" --user 2>/dev/null || \
  pip3 install -q -r "$TARGET/scripts/requirements.txt" 2>/dev/null || \
  echo "⚠ Python依赖安装失败，请手动运行: pip3 install python-docx"
  echo "✓ Python 依赖已安装"
elif command -v pip &> /dev/null; then
  pip install -q -r "$TARGET/scripts/requirements.txt" --user 2>/dev/null || \
  echo "⚠ Python依赖安装失败，请手动运行: pip install python-docx"
  echo "✓ Python 依赖已安装"
else
  echo "⚠ 未找到 pip，请手动安装: pip install python-docx"
fi

# 4. 检测并安装搜索增强（anysearch）
echo ""
echo "正在检测搜索增强组件..."
ANYSEARCH_DIR="$SKILL_DIR/anysearch"
if [ -f "$ANYSEARCH_DIR/scripts/anysearch_cli.py" ]; then
  echo "✓ 检测到已安装 anysearch 搜索增强"
else
  echo "  正在安装搜索增强组件 (anysearch)..."

  # 尝试从同级目录复制（如果是从 claude-skills 仓库一起下载的）
  if [ -f "$SCRIPT_DIR/../anysearch/scripts/anysearch_cli.py" ]; then
    mkdir -p "$ANYSEARCH_DIR"
    cp -r "$SCRIPT_DIR/../anysearch/"* "$ANYSEARCH_DIR/"
    echo "✓ 搜索增强已从本地复制安装"
  # 尝试从 GitHub 克隆
  elif command -v git &> /dev/null; then
    git clone --depth 1 https://github.com/hesongshuaige/claude-skills.git /tmp/claude-skills-anysearch 2>/dev/null && \
    mkdir -p "$ANYSEARCH_DIR" && \
    cp -r /tmp/claude-skills-anysearch/anysearch/* "$ANYSEARCH_DIR/" 2>/dev/null && \
    rm -rf /tmp/claude-skills-anysearch && \
    echo "✓ 搜索增强已从 GitHub 安装" || \
    echo "⚠ 搜索增强安装失败（网络原因），技能将以基础模式运行"
  else
    echo "⚠ 未找到 git，无法自动安装搜索增强"
  fi

  # 验证安装
  if [ -f "$ANYSEARCH_DIR/scripts/anysearch_cli.py" ]; then
    echo "✓ 搜索增强已就绪"
  else
    echo ""
    echo "  ┌──────────────────────────────────────────────────────┐"
    echo "  │ 搜索增强未安装。技能将使用平台内置搜索工具运行。    │"
    echo "  │ 搜索质量会降低（缺少招聘平台数据、工商交叉验证）。  │"
    echo "  │ 推荐手动安装：                                      │"
    echo "  │   git clone https://github.com/hesongshuaige/claude-skills.git"
    echo "  │   cp -r claude-skills/anysearch $ANYSEARCH_DIR"
    echo "  └──────────────────────────────────────────────────────┘"
  fi
fi

# 5. 创建输出目录
DELIVERABLES="$HOME/deliverables"
mkdir -p "$DELIVERABLES"
echo ""
echo "✓ 输出目录: $DELIVERABLES"

# 6. 完成
echo ""
echo "======================================"
echo "  ✅ 安装完成！"
echo "======================================"
echo ""
echo "下一步："
echo "  1. 编辑配置文件: vim $TARGET/config.yaml"
echo "  2. 对 AI Agent 说：帮我研判XX企业"
echo ""
echo "支持的命令示例："
echo "  Claude Code:  /go 帮我研判XX企业"
echo "  Codex CLI:    研判一下XX企业"
echo "  通用:         使用go技能分析XX公司能不能投"
echo ""
echo "输出文件将保存到: $DELIVERABLES/"
