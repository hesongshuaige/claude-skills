#!/usr/bin/env bash
# skillup 飞书上传：把 md 文档传到 AI 提示词工程库，挂到库根，输出 URL。
# 用法: ./upload.sh "<文档标题>" <md文件路径>
# 必须先配置 SKILLUP_SPACE_ID（环境变量 或 ~/.config/skillup.conf）。
set -e

# 读配置文件（如存在）
CONF="$HOME/.config/skillup.conf"
[ -f "$CONF" ] && source "$CONF"

SPACE="${SKILLUP_SPACE_ID:?错误: 未配置 SKILLUP_SPACE_ID（环境变量 或 ~/.config/skillup.conf）}"
TITLE="${1:?用法: upload.sh <标题> <md文件>}"
MD="${2:?用法: upload.sh <标题> <md文件>}"

if [ ! -f "$MD" ]; then echo "错误: 文件不存在 $MD" >&2; exit 1; fi

# 1. 上传 markdown（stdin 传内容，绕开 --file 的相对路径限制）
FT=$(cat "$MD" | lark-cli markdown +create --as user --content - --name "$TITLE.md" --format json 2>/dev/null | jq -r '.data.file_token')
if [ -z "$FT" ] || [ "$FT" = "null" ]; then
  echo "错误: 上传 markdown 失败" >&2; exit 1
fi

# 2. 挂到库根
NT=$(lark-cli wiki +move --as user --obj-type file --obj-token "$FT" --target-space-id "$SPACE" --format json 2>/dev/null | jq -r '.data.node_token')
if [ -z "$NT" ] || [ "$NT" = "null" ]; then
  echo "错误: 挂到 wiki 失败" >&2; exit 1
fi

echo "URL=https://my.feishu.cn/wiki/$NT"
echo "NODE_TOKEN=$NT"
echo "TITLE=$TITLE"

# 3. 索引更新提示（AI 用 markdown +overwrite 调用，参考 REFERENCE.md §四）
if [ -n "$SKILLUP_INDEX_TOKEN" ]; then
  echo "INDEX_TOKEN=$SKILLUP_INDEX_TOKEN"
  echo "提示: 索引更新用 -> lark-cli markdown +overwrite --as user --file-token $SKILLUP_INDEX_TOKEN --content -  <索引md>"
fi
