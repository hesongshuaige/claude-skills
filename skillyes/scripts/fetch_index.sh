#!/usr/bin/env bash
# skillyes - 拉飞书「AI提示词工程库」索引页全文
# 解析 6 字段交给上层 LLM（索引页是 agent 友好 markdown，直接读就能匹配，不脆解析）
# 用法：bash fetch_index.sh  →  stdout 输出索引页 markdown 全文
#
# 配置（去硬编码，二选一）：
#   A) 环境变量 SKILLYES_INDEX_TOKEN（= 索引页 file_token）
#   B) ~/.config/skillyes.conf 里的 SKILLYES_INDEX_TOKEN=...
set -euo pipefail

# lark-cli 装在 ~/.npm-global/bin（非交互 shell 默认 PATH 找不到，必须加）
export PATH="$HOME/.npm-global/bin:$PATH"

CONF="$HOME/.config/skillyes.conf"
# 先从 conf 文件读（env 优先，conf 兜底）
if [ -z "${SKILLYES_INDEX_TOKEN:-}" ] && [ -f "$CONF" ]; then
  while IFS='=' read -r k v; do
    [ -z "$k" ] && continue
    case "$k" in
      SKILLYES_INDEX_TOKEN) SKILLYES_INDEX_TOKEN="$v" ;;
      SKILLYES_SPACE_ID)   SKILLYES_SPACE_ID="$v" ;;
    esac
  done < "$CONF"
fi

if [ -z "${SKILLYES_INDEX_TOKEN:-}" ]; then
  echo "✗ 未配置 SKILLYES_INDEX_TOKEN（索引页 file_token）。" >&2
  echo "  方式A: export SKILLYES_INDEX_TOKEN=<索引页file_token>" >&2
  echo "  方式B: 写 ~/.config/skillyes.conf，加一行 SKILLYES_INDEX_TOKEN=..." >&2
  exit 1
fi

# fetch 索引页 → 取 .data.content（不是顶层 .content）
lark-cli markdown +fetch --file-token "$SKILLYES_INDEX_TOKEN" \
  | jq -r '.data.content'
