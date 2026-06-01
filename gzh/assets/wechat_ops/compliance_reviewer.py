#!/usr/bin/env python3
"""Review a Zhuge Capital WeChat draft for compliance and publication risk."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import time
from typing import Any

from topic_collector import first_select


ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
DRAFT_PENDING_VIEW_ID = "vewBXBtFGA"

READ_FIELDS = [
    "文章主题",
    "服务主线",
    "目标读者",
    "核心观点",
    "事实核验状态",
    "投资部确认",
    "合规结论",
    "审稿状态",
    "AI预审结论",
    "AI预审理由",
    "可对外表达程度",
    "内部确认清单",
    "初稿链接",
    "初稿生成状态",
    "初稿生成说明",
    "表达边界",
    "审稿意见/复盘结论",
]

FORBIDDEN_TERMS = {
    "公开募集": "可能构成面向不特定对象募集或基金产品推介风险",
    "面向社会募集": "可能构成公开募集风险",
    "保本": "私募基金和投资表达中不得出现保本口径",
    "兜底": "私募基金和投资表达中不得出现兜底口径",
    "承诺收益": "不得承诺投资收益",
    "保证收益": "不得保证收益",
    "稳赚": "明显收益承诺或夸大宣传",
    "年化收益": "容易被理解为收益推介",
    "固定收益": "容易被理解为产品收益推介",
    "认购": "容易被理解为基金募集或产品销售",
}

LEADER_TERMS = ["习近平", "习近平总书记", "党中央", "国务院"]
INVESTMENT_PROMISE_TERMS = ["一定投资", "立即投资", "优先投资", "承诺投资", "确保投资"]
PUBLIC_SIGNAL_TERMS = ["欢迎", "交流", "对接", "合作机构", "项目方"]


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
        cmd.extend(["--view-id", DRAFT_PENDING_VIEW_ID, "--limit", "1"])
    cmd.extend(["--format", "json"])
    for field in READ_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list") or data.get("record_not_found"):
        raise RuntimeError("没有待合规审查的初稿记录")
    row = dict(zip(data["fields"], data["data"][0]))
    row["record_id"] = data["record_id_list"][0]
    return row


def normalize_doc_url(value: str) -> str:
    value = value or ""
    match = re.search(r"\((https?://[^)]+)\)", value)
    if match:
        return match.group(1)
    match = re.search(r"https?://\S+", value)
    return match.group(0).rstrip(")") if match else value


def fetch_doc_text(doc_url: str) -> str:
    data = run_lark_json(
        [
            "lark-cli",
            "docs",
            "+fetch",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--doc",
            doc_url,
            "--doc-format",
            "xml",
        ]
    )
    content = data["data"]["document"]["content"]
    text = re.sub(r"<br\s*/?>", "\n", content)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def is_negative_context(text: str, term: str) -> bool:
    for match in re.finditer(re.escape(term), text):
        start = max(0, match.start() - 45)
        end = min(len(text), match.end() + 45)
        window = text[start:end]
        if any(marker in window for marker in ("不得", "不能", "禁止", "避免", "不出现", "不可", "不是", "风险", "边界")):
            continue
        return False
    return True


def term_hits(text: str, terms: dict[str, str] | list[str]) -> list[str]:
    items = terms.keys() if isinstance(terms, dict) else terms
    hits: list[str] = []
    for term in items:
        lines = [line for line in text.splitlines() if term in line]
        positive_lines = [
            line
            for line in lines
            if not any(marker in line for marker in ("不得", "不能", "禁止", "避免", "不出现", "不可", "不是", "风险", "边界"))
        ]
        if positive_lines and not is_negative_context(text, term):
            hits.append(term)
    return hits


def build_review(record: dict[str, Any], draft_text: str) -> dict[str, Any]:
    fact_status = first_select(record.get("事实核验状态"))
    investment_confirm = first_select(record.get("投资部确认"))
    precheck = first_select(record.get("AI预审结论"))
    draft_status = first_select(record.get("初稿生成状态"))
    public_level = first_select(record.get("可对外表达程度"))
    forbidden_hits = term_hits(draft_text, FORBIDDEN_TERMS)
    promise_hits = term_hits(draft_text, INVESTMENT_PROMISE_TERMS)
    leader_hits = [term for term in LEADER_TERMS if term in draft_text]

    issues: list[str] = []
    fixes: list[str] = []

    if forbidden_hits:
        issues.append(f"出现高风险投资或募集表述：{'、'.join(forbidden_hits)}。")
        fixes.append("删除高风险词，不能出现公开募集、收益承诺、保本兜底、基金产品销售等表达。")
    if promise_hits:
        issues.append(f"出现可能被理解为投资承诺的表述：{'、'.join(promise_hits)}。")
        fixes.append("把投资承诺类表达改为“在合规边界内交流、对接、协同”。")
    if leader_hits:
        issues.append(f"出现上级或领导表述：{'、'.join(sorted(set(leader_hits)))}，必须按权威原文核验。")
        fixes.append("凡涉及中央、省、市、区政策和领导表述，正式发布前必须逐字核对权威来源。")
    if fact_status != "已核验":
        issues.append(f"事实核验状态为“{fact_status}”，政策发文字号、发布日期、发布机关、来源链接仍需复核。")
        fixes.append("综合部先核验政策原文和来源链接，再进入部长审。")
    if investment_confirm == "待确认":
        issues.append("投资部确认仍为“待确认”，诸葛资本产业关注方向、项目方承接口径不能直接对外发布。")
        fixes.append("把“内部确认清单”发给投资部，只确认方向、口径和敏感点，不要求投资部重写全文。")
    if precheck == "必须人工确认":
        issues.append("AI（人工智能）预审结论为“必须人工确认”，当前稿件只能作为内部讨论稿。")
    if draft_status == "已生成待确认":
        issues.append("初稿生成状态为“已生成待确认”，流程上不应直接进入发布。")
    if public_level == "限定表达":
        issues.append("可对外表达程度为“限定表达”，应控制在公开政策趋势、区域资源、产业服务价值，不能扩大为投资邀约。")

    if not issues:
        issues.append("未发现明显公开募集、收益承诺、保本兜底、未公开项目信息披露等硬伤。")
        fixes.append("仍需保留人工终审，特别是政策引用和公司真实口径。")

    if forbidden_hits or promise_hits:
        risk_level = "高"
        conclusion = "不建议发"
        status = "需重写"
    elif investment_confirm == "待确认" or precheck == "必须人工确认" or fact_status != "已核验":
        risk_level = "中"
        conclusion = "修改后可发"
        status = "待修改"
    else:
        risk_level = "低"
        conclusion = "能发"
        status = "已审查"

    review_note = (record.get("审稿意见/复盘结论") or "").rstrip()
    if review_note:
        review_note += "\n"
    review_note += f"已完成合规审查：{conclusion}，风险等级：{risk_level}。"

    return {
        "合规结论": conclusion,
        "合规审查状态": status,
        "合规风险等级": risk_level,
        "合规问题清单": "\n".join(f"{idx}. {item}" for idx, item in enumerate(issues, start=1)),
        "合规修改建议": "\n".join(f"{idx}. {item}" for idx, item in enumerate(fixes, start=1)),
        "发布前必核事项": (
            "1. 政策原文、发文字号、发布日期、发布机关、来源链接。\n"
            "2. 投资部确认产业关注方向、项目方承接口径、机构合作口径。\n"
            "3. 不出现公开募集、承诺收益、保本兜底、具体投资承诺、未公开项目和交易信息。\n"
            "4. 何松终审确认标题、正文、合作入口和发布时机。"
        ),
        "审稿意见/复盘结论": review_note,
    }


def write_review(record_id: str, patch: dict[str, Any]) -> None:
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
    parser = argparse.ArgumentParser(description="Review a Zhuge Capital WeChat draft for compliance.")
    parser.add_argument("--write", action="store_true", help="write compliance review into Feishu Base")
    parser.add_argument("--record-id", default="", help="process a specific article production record")
    args = parser.parse_args()

    record = get_candidate(args.record_id)
    doc_url = normalize_doc_url(record.get("初稿链接") or "")
    if not doc_url:
        raise RuntimeError("当前记录没有初稿链接，无法做合规审查")
    draft_text = fetch_doc_text(doc_url)
    patch = build_review(record, draft_text)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "article": record.get("文章主题"), "review": patch}, ensure_ascii=False, indent=2))
        return 0
    write_review(record["record_id"], patch)
    time.sleep(0.5)
    print(json.dumps({"ok": True, "record_id": record["record_id"], "article": record.get("文章主题"), "合规结论": patch["合规结论"], "合规风险等级": patch["合规风险等级"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
