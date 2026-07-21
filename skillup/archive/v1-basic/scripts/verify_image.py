#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skillup 生图类验证：用 image-01 出图，下载到本地供 AI/人工判断。

用法:
  python3 verify_image.py --prompt "海报背景描述" --out /tmp/test.png [--ratio 16:9]

说明: 生图质量无法自动判定，脚本只负责出图。AI 看 downloaded 图后判断
是否符合（留白/配色/质感/不糊），决定该场景通过或调提示词重试。
生图 prompt 禁文字/人物/logo（会糊）。
"""
import argparse, json, os, sys, urllib.request

BASE = "https://api.minimaxi.com/v1"

def load_key():
    k = os.environ.get("MINIMAX_API_KEY")
    if k:
        return k
    for p in (os.path.expanduser("~/.secrets/mm.env"), ".secrets/mm.env"):
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                if ln.strip().startswith("export MINIMAX_API_KEY="):
                    return ln.strip().split("=", 1)[1].strip().strip("'\"")
    sys.exit("错误: 找不到 MINIMAX_API_KEY（环境变量 或 ~/.secrets/mm.env 或 ./.secrets/mm.env）")

def gen(prompt, ratio):
    key = load_key()
    body = json.dumps({"model": "image-01", "prompt": prompt, "aspect_ratio": ratio,
                       "n": 1, "prompt_optimizer": True, "response_format": "url"}).encode("utf-8")
    req = urllib.request.Request(BASE + "/image_generation", data=body,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        res = json.load(r)
    if res.get("base_resp", {}).get("status_code", 0) != 0:
        sys.exit("生图失败: " + json.dumps(res, ensure_ascii=False)[:300])
    return res["data"]["image_urls"]

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "skillup/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def main():
    ap = argparse.ArgumentParser(description="skillup 生图验证（image-01）")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, help="输出路径 .png/.jpg")
    ap.add_argument("--ratio", default="16:9",
                    choices=["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"])
    args = ap.parse_args()
    urls = gen(args.prompt, args.ratio)
    n = download(urls[0], args.out)
    print(json.dumps({"ok": True, "out": args.out, "bytes": n,
                      "note": "图已下载本地，AI 看图判断是否符合；URL 仅 24h 有效"},
                     ensure_ascii=False))

if __name__ == "__main__":
    main()
