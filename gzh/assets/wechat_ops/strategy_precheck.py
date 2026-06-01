#!/usr/bin/env python3
"""Precheck a Zhuge Capital WeChat article strategy before drafting."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any

from topic_collector import first_select


ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
STRATEGY_PENDING_VIEW_ID = "vewqTA0oTd"

READ_FIELDS = [
    "文章主题",
    "服务主线",
    "目标读者",
    "核心观点",
    "资料包摘要",
    "事实核验状态",
    "投资部确认",
    "合规结论",
    "审稿状态",
    "标题备选",
    "文章结构",
    "表达边界",
    "策略卡结论",
    "策略卡状态",
    "承接动作",
    "分发对象",
    "审稿意见/复盘结论",
]

FORBIDDEN_TERMS = [
    "保本",
    "兜底",
    "承诺收益",
    "保证收益",
    "稳赚",
    "公开募集",
    "面向社会募集",
    "立即投资",
    "一定投资",
]


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def get_pending_strategy(record_id: str = "") -> dict[str, Any]:
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
        cmd.extend(["--view-id", STRATEGY_PENDING_VIEW_ID, "--limit", "1"])
    cmd.extend(["--format", "json"])
    for field in READ_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list") or data.get("record_not_found"):
        raise RuntimeError("没有待 AI 预审的策略卡记录")
    row = dict(zip(data["fields"], data["data"][0]))
    row["record_id"] = data["record_id_list"][0]
    return row


def joined(record: dict[str, Any], *fields: str) -> str:
    parts: list[str] = []
    for field in fields:
        value = record.get(field)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value:
            parts.append(str(value))
    return "\n".join(parts)


def detect_forbidden_terms(record: dict[str, Any]) -> list[str]:
    text = joined(record, "核心观点", "资料包摘要", "标题备选", "文章结构", "策略卡结论")
    risk_hint_markers = ("不得", "不能", "禁止", "避免", "风险提醒", "不能写", "合规", "边界", "不出现")
    proposed_lines = [
        line
        for line in text.splitlines()
        if line.strip() and not any(marker in line for marker in risk_hint_markers)
    ]
    proposed_text = "\n".join(proposed_lines)
    return [term for term in FORBIDDEN_TERMS if term in proposed_text]


def confirmation_list(record: dict[str, Any], forbidden_hits: list[str]) -> str:
    theme = record.get("文章主题") or "当前文章"
    service_line = first_select(record.get("服务主线"))
    readers = "、".join(record.get("目标读者") or [])
    items = [
        f"1. 请投资部确认：{theme}这个方向，是否符合诸葛资本当前可公开表达的产业关注边界。",
        "2. 请投资部确认：能否使用“用国资基金工具连接项目、政策、产业资源和合作机构”这一口径。",
        "3. 请投资部确认：是否可以对外释放“欢迎硬科技、智能制造、AI（人工智能）应用类项目交流”的温和合作信号。",
        "4. 请综合部核验：政策发布机关、发文字号、发布日期、政策原文链接是否准确；引用中央、省、市、区政策时必须按原文表述。",
        "5. 请终审确认：全文不出现公开募资、承诺投资、承诺收益、保本兜底、夸大投资能力、未公开项目或交易信息。",
    ]
    if service_line == "领导认可型":
        items.append("6. 请确认：是否需要加入服务区委区政府中心工作的表达，但不要写成空泛表态。")
    if "项目方" in readers:
        items.append("6. 请确认：项目方承接口径只写“交流、对接、协同”，不能写成投资邀约或基金推介。")
    if "投资机构" in readers:
        items.append("7. 请确认：机构合作口径只写产业协同和项目交流，不能写成对外募资。")
    if forbidden_hits:
        items.append(f"8. 当前材料命中高风险词：{'、'.join(forbidden_hits)}，必须删除或改写后再进入初稿。")
    return "\n".join(items)


def build_precheck(record: dict[str, Any]) -> dict[str, Any]:
    fact_status = first_select(record.get("事实核验状态"))
    investment_confirm = first_select(record.get("投资部确认"))
    strategy_status = first_select(record.get("策略卡状态"))
    compliance = first_select(record.get("合规结论"))
    forbidden_hits = detect_forbidden_terms(record)

    reasons: list[str] = []
    if fact_status in {"未核验", "有疑点"}:
        reasons.append(f"事实核验状态为“{fact_status}”，不能直接进入可发布稿。")
    elif fact_status == "部分核验":
        reasons.append("事实核验状态为“部分核验”，公开政策可写，但政策细节和本地连接仍需复核。")

    if investment_confirm == "待确认":
        reasons.append("投资部确认仍为“待确认”，公司真实产业关注边界和对外合作口径不能由 AI（人工智能）代替确认。")
    elif investment_confirm in {"慎写", "不建议写"}:
        reasons.append(f"投资部确认状态为“{investment_confirm}”，需要按更高风险处理。")

    if strategy_status == "待确认":
        reasons.append("策略卡状态为“待确认”，说明当前还没有进入初稿的充分条件。")

    if compliance == "未审查":
        reasons.append("合规结论为“未审查”，后续必须走合规清单。")

    if forbidden_hits:
        reasons.append(f"材料中出现高风险词：{'、'.join(forbidden_hits)}。")

    if investment_confirm in {"不建议写"} or forbidden_hits:
        conclusion = "不建议写"
        public_level = "暂不表达"
    elif investment_confirm == "待确认" or fact_status in {"未核验", "有疑点"}:
        conclusion = "必须人工确认"
        public_level = "限定表达"
    elif fact_status == "部分核验" or compliance == "未审查":
        conclusion = "慎写"
        public_level = "限定表达"
    else:
        conclusion = "通过"
        public_level = "可公开表达"

    if not reasons:
        reasons.append("未发现明显策略和合规前置障碍，但仍需保留人工终审。")

    modify_advice = (
        "建议初稿只写三类内容：公开政策趋势、区域产业资源、诸葛资本作为国资基金平台的协同服务价值。\n"
        "建议删掉或弱化三类内容：具体投资偏好、具体项目判断、未经授权的已投案例或合作方信息。\n"
        "建议承接口径统一为：欢迎相关项目方、机构在合规边界内交流产业机会；不得写成募集、推介、投资承诺或收益承诺。"
    )

    review_note = record.get("审稿意见/复盘结论") or ""
    review_note = review_note.rstrip()
    if review_note:
        review_note += "\n"
    review_note += f"已完成 AI（人工智能）策略预审：{conclusion}。"

    return {
        "AI预审结论": conclusion,
        "AI预审理由": "\n".join(reasons),
        "可对外表达程度": public_level,
        "内部确认清单": confirmation_list(record, forbidden_hits),
        "修改建议": modify_advice,
        "AI预审状态": "已预审",
        "审稿意见/复盘结论": review_note,
    }


def write_precheck(record_id: str, patch: dict[str, Any]) -> None:
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
    parser = argparse.ArgumentParser(description="Precheck a pending Zhuge Capital WeChat strategy card.")
    parser.add_argument("--write", action="store_true", help="write precheck result into Feishu Base")
    parser.add_argument("--record-id", default="", help="process a specific article production record")
    args = parser.parse_args()

    record = get_pending_strategy(args.record_id)
    patch = build_precheck(record)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "article": record.get("文章主题"), "precheck": patch}, ensure_ascii=False, indent=2))
        return 0

    write_precheck(record["record_id"], patch)
    time.sleep(0.5)
    print(json.dumps({"ok": True, "record_id": record["record_id"], "article": record.get("文章主题"), "AI预审结论": patch["AI预审结论"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
