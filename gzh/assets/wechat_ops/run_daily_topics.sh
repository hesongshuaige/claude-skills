#!/usr/bin/env bash
set -euo pipefail

export PATH="/root/.nvm/versions/node/v22.22.1/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

mkdir -p /root/zhuge-corp/wechat_ops/logs

/usr/bin/python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode daily --write --limit 8 --top 3 \
  >> /root/zhuge-corp/wechat_ops/logs/daily_topics.log 2>&1
