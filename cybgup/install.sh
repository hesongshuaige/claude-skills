#!/bin/bash
# CYBGUP 技能安装脚本 — 自动检测 5 个平台
# 用法: cd cybgup && bash install.sh

SKILL_NAME="cybgup"
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  CYBGUP 技能安装"
echo "  国资以投促招项目初步研判报告生成器"
echo "=========================================="
echo ""

# 检测目标平台并安装
installed=0

# Claude Code
if [ -d "$HOME/.claude/skills" ]; then
  cp -r "$CURRENT_DIR" "$HOME/.claude/skills/$SKILL_NAME"
  echo "[OK] Claude Code: $HOME/.claude/skills/$SKILL_NAME"
  installed=1
fi

# Codex
if [ -d "$HOME/.codex/skills" ]; then
  cp -r "$CURRENT_DIR" "$HOME/.codex/skills/$SKILL_NAME"
  echo "[OK] Codex: $HOME/.codex/skills/$SKILL_NAME"
  installed=1
fi

# OpenClaw
if [ -d "$HOME/.openclaw/skills" ]; then
  cp -r "$CURRENT_DIR" "$HOME/.openclaw/skills/$SKILL_NAME"
  echo "[OK] OpenClaw: $HOME/.openclaw/skills/$SKILL_NAME"
  installed=1
fi

# Hermes
if [ -d "$HOME/.hermes/skills" ]; then
  cp -r "$CURRENT_DIR" "$HOME/.hermes/skills/$SKILL_NAME"
  echo "[OK] Hermes: $HOME/.hermes/skills/$SKILL_NAME"
  installed=1
fi

# Agents (通用)
if [ -d "$HOME/.agents/skills" ]; then
  cp -r "$CURRENT_DIR" "$HOME/.agents/skills/$SKILL_NAME"
  echo "[OK] Agents: $HOME/.agents/skills/$SKILL_NAME"
  installed=1
fi

if [ $installed -eq 0 ]; then
  echo "[WARN] 未检测到已安装的 Agent 平台。"
  echo "  请手动复制 $SKILL_NAME 目录到你的技能目录："
  echo "  Claude Code: ~/.claude/skills/"
  echo "  Codex:       ~/.codex/skills/"
  echo "  OpenClaw:    ~/.openclaw/skills/"
  echo "  Hermes:      ~/.hermes/skills/"
  echo "  Agents:      ~/.agents/skills/"
fi

echo ""
echo "安装完成。"
echo "依赖：python-docx（用于公文 Word 导出）"
echo "  pip install python-docx"
echo ""
echo "推荐搭配安装："
echo "  playwright-core（用于浏览器优先搜索策略）"
echo "  npm install playwright-core"