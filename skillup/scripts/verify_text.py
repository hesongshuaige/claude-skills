#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skillup 文本类场景批量验证。

用法:
  python3 verify_text.py scenes.json

scenes.json 格式:
  [
    {"name":"①场景名", "sys":"系统提示词", "users":["开场白","故意答错的话","答对的话"]},
    ...
  ]

输出: 每场景 3 轮原始对话 + 启发式机制判定（✓/✗），最后汇总。
启发式只筛明显失败，最终是否采用由 AI 看原文决定。
"""
import json, os, sys, urllib.request

BASE = "https://api.minimaxi.com/v1"

def load_key():
    k = os.environ.get("MINIMAX_API_KEY")
    if k:
        return k
    candidates = [
        os.path.expanduser("~/.secrets/mm.env"),
        os.path.abspath(".secrets/mm.env"),
    ]
    for p in candidates:
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                if ln.strip().startswith("export MINIMAX_API_KEY="):
                    return ln.strip().split("=", 1)[1].strip().strip("'\"")
    sys.exit("错误: 找不到 MINIMAX_API_KEY（环境变量 或 ~/.secrets/mm.env 或 ./.secrets/mm.env）")

def chat(msgs, max_tokens=2800):
    body = json.dumps({"model": "MiniMax-M3", "messages": msgs, "max_tokens": max_tokens}).encode("utf-8")
    req = urllib.request.Request(BASE + "/chat/completions", data=body,
            headers={"Authorization": "Bearer " + load_key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            res = json.load(r)
    except Exception as e:
        return f"[CALL ERROR: {e}]", False
    if res.get("base_resp", {}).get("status_code", 0) != 0:
        return f"[API ERROR: {json.dumps(res, ensure_ascii=False)[:200]}]", False
    c = res["choices"][0]["message"]["content"]
    if "</think>" in c:
        b = c.split("</think>", 1)[1].strip()
        return (b if b else "[正文空，think 吃光]"), True
    return c.strip(), True

def judge(tag, reply):
    """启发式判定单轮机制。返回 (ok, reason)。"""
    has_q = ("？" in reply) or ("?" in reply)
    bullets = any(x in reply for x in ["\n1.", "\n2.", "①", "②", "一、", "第一，", "第一、", "\n- "])
    if "[CALL ERROR" in reply or "[API ERROR" in reply or "正文空" in reply:
        return False, "调用失败/空输出"
    if tag == "开场":
        if has_q and not bullets:
            return True, "探测+一次一问+无分点"
        if has_q:
            return True, "有问号(可能分点，需人工确认)"
        return False, "没问问题，可能直接开讲"
    if tag == "答错":
        give_answer = any(x in reply for x in ["正确答案是", "正确的是", "答案就是", "其实就是", "公式是"])
        if has_q and not give_answer:
            return True, "反问引导+没直接给答案"
        if has_q:
            return False, "反问了但疑似直接给答案"
        return False, "没反问引导"
    if tag == "答对":
        affirm = any(x in reply for x in ["对", "漂亮", "没错", "正确", "哎呦", "好", "诶", "棒", "摸到", "嗨"])
        if affirm and has_q:
            return True, "肯定+追问更深"
        if has_q:
            return True, "追问(肯定不明显，需人工确认)"
        return False, "没追问更深"
    return True, ""

def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python3 verify_text.py scenes.json")
    scenes = json.load(open(sys.argv[1], encoding="utf-8"))
    results = []
    for s in scenes:
        name, sysmsg, users = s["name"], s["sys"], s["users"]
        print(f"\n{'#' * 60}\n# {name}\n{'#' * 60}")
        msgs = [{"role": "system", "content": sysmsg}]
        rounds_ok = []
        for i, u in enumerate(users):
            tag = ["开场", "答错", "答对"][i]
            msgs.append({"role": "user", "content": u})
            reply, ok_call = chat(msgs)
            msgs.append({"role": "assistant", "content": reply})
            ok, reason = judge(tag, reply)
            rounds_ok.append(ok)
            print(f"\n--- T{i+1}({tag}) [{'✓' if ok else '✗'}] {reason} ---")
            print(f"👤: {u}\n🤖: {reply}")
        passed = all(rounds_ok)
        results.append({"name": name, "passed": passed, "rounds": rounds_ok})
        print(f"\n>>> {name}: {'✅ 通过' if passed else '❌ 未通过'}")
    print(f"\n{'=' * 60}\n验证汇总:")
    for r in results:
        print(f"  {'✅' if r['passed'] else '❌'} {r['name']}")
    out = "/tmp/skillup_verify_result.json"
    json.dump(results, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n结果已写 {out}")

if __name__ == "__main__":
    main()
