#!/usr/bin/env python3
"""Generate confirmation packets for Zhuge Capital WeChat article blockers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from typing import Any


ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
BLOCKED_VIEW_ID = "vew7oRqsfP"

READ_FIELDS = [
    "文章主题",
    "初稿链接",
    "内部确认清单",
    "送审阻断事项",
    "送审判断",
    "下一步处理动作",
    "合规问题清单",
    "合规修改建议",
    "发布前必核事项",
    "来源材料链接",
    "资料包摘要",
    "审稿意见/复盘结论",
]


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def get_candidate(record_id: str = "") -> dict[str, Any]:
    cmd = [
        "lark-cli",
        "base",
        "+record-get" if record_id else "+record-list",
        "--as",
        "user",
        "--base-token",
        ARTICLE_BASE_TOKEN,
        "--table-id",
        ARTICLE_TABLE_ID,
    ]
    if record_id:
        cmd.extend(["--record-id", record_id])
    else:
        cmd.extend(["--view-id", BLOCKED_VIEW_ID, "--limit", "1"])
    cmd.extend(["--format", "json"])
    for field in READ_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list") or data.get("record_not_found"):
        raise RuntimeError("没有需要生成确认推进包的文章记录")
    row = dict(zip(data["fields"], data["data"][0]))
    row["record_id"] = data["record_id_list"][0]
    return row


def normalize_url(value: str) -> str:
    value = value or ""
    match = re.search(r"\((https?://[^)]+)\)", value)
    if match:
        return match.group(1)
    match = re.search(r"https?://\S+", value)
    return match.group(0).rstrip(")") if match else value


def lines(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


def strip_numbering(value: str) -> str:
    text = value.strip()
    while True:
        cleaned = re.sub(r"^\d+[.、]\s*", "", text).strip()
        if cleaned == text:
            return cleaned
        text = cleaned


def first_select(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    return "" if value is None else str(value)


def investment_questions(record: dict[str, Any]) -> list[str]:
    source = lines(record.get("内部确认清单"))
    picked = [
        item
        for item in source
        if any(keyword in item for keyword in ("投资部", "产业关注", "项目方", "机构合作", "承接口径", "敏感点", "可公开表达"))
    ]
    defaults = [
        "请确认该文章方向是否符合诸葛资本当前可公开表达的产业关注边界。",
        "请确认是否可以使用“用国资基金工具连接项目、政策、产业资源和合作机构”这一口径。",
        "请确认项目方承接口径是否只能写“交流、对接、协同”，不能写成投资邀约或基金推介。",
        "请确认是否存在不宜公开的项目、合作方、交易、投决或内部信息。",
    ]
    result = picked or defaults
    return [strip_numbering(item) for item in result[:6]]


def fact_check_items(record: dict[str, Any]) -> list[str]:
    source = lines(record.get("发布前必核事项")) + lines(record.get("合规修改建议"))
    picked = [
        item
        for item in source
        if any(keyword in item for keyword in ("政策", "发文字号", "发布日期", "发布机关", "来源链接", "原文"))
    ]
    defaults = [
        "核验政策原文链接是否能打开，来源是否为权威官方网站。",
        "核验发布机关、发文字号、成文日期、发布日期是否与原文一致。",
        "核验文章中引用的政策名称和表述是否按原文表达。",
        "核验是否涉及中央、省、市、区政策和领导表述；如涉及，必须按权威原文逐字核对。",
    ]
    result = picked or defaults
    return [strip_numbering(item) for item in result[:6]]


def build_investment_message(record: dict[str, Any]) -> str:
    title = record.get("文章主题") or "公众号文章"
    draft_url = normalize_url(record.get("初稿链接") or "")
    questions = investment_questions(record)
    question_text = "\n".join(f"{idx}. {item}" for idx, item in enumerate(questions, start=1))
    return (
        f"各位好，综合部这边准备围绕《{title}》形成一篇公众号稿件，目前只需要投资部帮忙确认方向和口径，不需要重写全文。\n\n"
        f"请重点确认以下事项：\n{question_text}\n\n"
        "请直接回复：可写 / 慎写 / 不建议写；如果慎写或不建议写，请简单说明不能公开表达的点。\n"
        f"初稿链接：{draft_url or '见飞书文章生产表'}"
    )


def build_general_checklist(record: dict[str, Any]) -> str:
    title = record.get("文章主题") or "公众号文章"
    source_url = normalize_url(record.get("来源材料链接") or "")
    draft_url = normalize_url(record.get("初稿链接") or "")
    items = fact_check_items(record)
    item_text = "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))
    return (
        f"文章《{title}》发布前，请综合部先做事实核验，核验完成后再送审。\n\n"
        f"核验清单：\n{item_text}\n\n"
        f"政策来源链接：{source_url or '见资料包摘要'}\n"
        f"初稿链接：{draft_url or '见飞书文章生产表'}\n\n"
        "核验完成后，请把“事实核验状态”改为“已核验”；如发现问题，先改初稿，再重新做合规审查。"
    )


def build_hesong_brief(record: dict[str, Any]) -> str:
    title = record.get("文章主题") or "公众号文章"
    blockers = lines(record.get("送审阻断事项"))
    actions = lines(record.get("下一步处理动作"))
    blocker_text = "\n".join(f"{idx}. {strip_numbering(item)}" for idx, item in enumerate(blockers[:5], start=1))
    action_text = "\n".join(f"{idx}. {strip_numbering(item)}" for idx, item in enumerate(actions[:5], start=1))
    return (
        f"《{title}》当前不是文章质量问题，主要卡在流程确认。\n\n"
        f"阻断事项：\n{blocker_text or '无'}\n\n"
        f"下一步动作：\n{action_text or '无'}\n\n"
        "建议先让投资部确认口径、综合部核验政策来源；两项完成后再升级为可送审稿。"
    )


def build_packet(record: dict[str, Any]) -> dict[str, Any]:
    if first_select(record.get("送审判断")) == "可送部长审":
        note = (record.get("审稿意见/复盘结论") or "").rstrip()
        if note:
            note += "\n"
        note += "前置确认已通过，当前可送部长审；无需生成阻断确认推进包。"
        return {
            "确认推进状态": "已确认",
            "何松处理简报": "当前稿件前置确认已通过，送审判断为“可送部长审”。建议进入部长审，部长审通过后再进入何松终审。",
            "审稿意见/复盘结论": note,
        }

    note = (record.get("审稿意见/复盘结论") or "").rstrip()
    if note:
        note += "\n"
    note += "已生成确认推进包。"
    return {
        "确认推进状态": "待确认",
        "投资部确认话术": build_investment_message(record),
        "综合部核验清单": build_general_checklist(record),
        "何松处理简报": build_hesong_brief(record),
        "审稿意见/复盘结论": note,
    }


def write_packet(record_id: str, patch: dict[str, Any]) -> None:
    cmd = [
        "lark-cli",
        "base",
        "+record-upsert",
        "--as",
        "user",
        "--base-token",
        ARTICLE_BASE_TOKEN,
        "--table-id",
        ARTICLE_TABLE_ID,
        "--record-id",
        record_id,
        "--json",
        json.dumps(patch, ensure_ascii=False),
    ]
    run_lark_json(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate confirmation packets for blocked WeChat drafts.")
    parser.add_argument("--write", action="store_true", help="write confirmation packet into Feishu Base")
    parser.add_argument("--record-id", default="", help="process a specific article production record")
    args = parser.parse_args()

    record = get_candidate(args.record_id)
    patch = build_packet(record)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "article": record.get("文章主题"), "packet": patch}, ensure_ascii=False, indent=2))
        return 0
    write_packet(record["record_id"], patch)
    time.sleep(0.5)
    print(json.dumps({"ok": True, "record_id": record["record_id"], "article": record.get("文章主题"), "确认推进状态": patch["确认推进状态"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
