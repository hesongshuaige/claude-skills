#!/usr/bin/env python3
"""Decide whether a Zhuge Capital WeChat draft can move to manager review."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any

from topic_collector import first_select


ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
COMPLIANCE_PENDING_VIEW_ID = "vewfdEctUb"

READ_FIELDS = [
    "文章主题",
    "初稿链接",
    "事实核验状态",
    "投资部确认",
    "AI预审结论",
    "可对外表达程度",
    "初稿生成状态",
    "合规结论",
    "合规审查状态",
    "合规风险等级",
    "合规问题清单",
    "合规修改建议",
    "发布前必核事项",
    "审稿状态",
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
        cmd.extend(["--view-id", COMPLIANCE_PENDING_VIEW_ID, "--limit", "1"])
    cmd.extend(["--format", "json"])
    for field in READ_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list") or data.get("record_not_found"):
        raise RuntimeError("没有待送审判断的文章记录")
    row = dict(zip(data["fields"], data["data"][0]))
    row["record_id"] = data["record_id_list"][0]
    return row


def build_route(record: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    actions: list[str] = []

    fact_status = first_select(record.get("事实核验状态"))
    investment_confirm = first_select(record.get("投资部确认"))
    ai_precheck = first_select(record.get("AI预审结论"))
    public_level = first_select(record.get("可对外表达程度"))
    draft_status = first_select(record.get("初稿生成状态"))
    compliance = first_select(record.get("合规结论"))
    compliance_status = first_select(record.get("合规审查状态"))
    risk = first_select(record.get("合规风险等级"))

    if not record.get("初稿链接"):
        blockers.append("还没有初稿链接。")
        actions.append("先生成公众号待审初稿。")
    if fact_status != "已核验":
        blockers.append(f"事实核验状态为“{fact_status}”，尚未达到送审条件。")
        actions.append("综合部核验政策原文、发文字号、发布日期、发布机关和来源链接，并把事实核验状态改为“已核验”。")
    if investment_confirm not in {"可写", "不需要"}:
        blockers.append(f"投资部确认为“{investment_confirm}”，尚未达到送审条件。")
        actions.append("把内部确认清单发给投资部，确认产业方向、项目方承接口径和敏感点；确认后改为“可写”或“不需要”。")
    if ai_precheck not in {"通过", "慎写"}:
        blockers.append(f"AI（人工智能）预审结论为“{ai_precheck}”，还不能直接送审。")
        actions.append("前置确认完成后，重新运行 AI（人工智能）预审或由何松确认是否解除阻断。")
    if public_level == "暂不表达":
        blockers.append("可对外表达程度为“暂不表达”。")
        actions.append("调整选题或表达边界后重新预审。")
    if draft_status != "已生成可送审":
        blockers.append(f"初稿生成状态为“{draft_status}”，还不是可送审稿。")
        actions.append("前置确认完成后，重新生成或升级为“已生成可送审”。")
    if compliance == "不建议发" or risk == "高":
        blockers.append(f"合规结论为“{compliance}”、风险等级为“{risk}”，不能送审。")
        actions.append("按合规修改建议重写或大改后重新审查。")
    elif compliance not in {"能发", "修改后可发"}:
        blockers.append(f"合规结论为“{compliance}”，还没有可送审依据。")
        actions.append("完成合规审查。")
    if compliance_status in {"待修改", "需重写"}:
        blockers.append(f"合规审查状态为“{compliance_status}”，说明仍有修改任务。")
        actions.append("综合部按合规修改建议处理后，再运行送审判断。")

    if blockers:
        route = "暂不送审"
        next_owner = "综合部/投资部"
        next_status = first_select(record.get("审稿状态")) or "待综合部初稿"
    else:
        route = "可送部长审"
        next_owner = "部长"
        next_status = "部长审"
        actions.append("已满足送审条件，可以进入部长审；部长审后再进入何松终审。")

    note = (record.get("审稿意见/复盘结论") or "").rstrip()
    if note:
        note += "\n"
    note += f"已完成送审判断：{route}。"

    patch: dict[str, Any] = {
        "送审判断": route,
        "送审阻断事项": "\n".join(f"{idx}. {item}" for idx, item in enumerate(blockers, start=1)) if blockers else "无",
        "下一步处理人": next_owner,
        "下一步处理动作": "\n".join(f"{idx}. {item}" for idx, item in enumerate(dict.fromkeys(actions), start=1)),
        "审稿意见/复盘结论": note,
    }
    if next_status:
        patch["审稿状态"] = next_status
    if route == "可送部长审":
        patch["合规审查状态"] = "已审查"
    return patch


def write_route(record_id: str, patch: dict[str, Any]) -> None:
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
    parser = argparse.ArgumentParser(description="Route a Zhuge Capital WeChat draft to manager review if ready.")
    parser.add_argument("--write", action="store_true", help="write route decision into Feishu Base")
    parser.add_argument("--record-id", default="", help="process a specific article production record")
    args = parser.parse_args()

    record = get_candidate(args.record_id)
    patch = build_route(record)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "article": record.get("文章主题"), "route": patch}, ensure_ascii=False, indent=2))
        return 0
    write_route(record["record_id"], patch)
    time.sleep(0.5)
    print(json.dumps({"ok": True, "record_id": record["record_id"], "article": record.get("文章主题"), "送审判断": patch["送审判断"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
