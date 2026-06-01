#!/usr/bin/env python3
"""Run and audit the Zhuge Capital WeChat operation pipeline."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable or "/usr/bin/python3"

TOPIC_BASE_TOKEN = "FUreb5ROTaYkoHsciK3c5h3unpP"
TOPIC_TABLE_ID = "tblyhgqm9SKvxMup"
ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
ASSET_BASE_TOKEN = "LcazbM9W6aA8i8sb57Bcl4Xanog"
ASSET_TABLE_ID = "tbl5wvjIo8ifQx8s"

TABLES = {
    "topics": {
        "base_token": TOPIC_BASE_TOKEN,
        "table_id": TOPIC_TABLE_ID,
        "title_field": "选题标题",
    },
    "articles": {
        "base_token": ARTICLE_BASE_TOKEN,
        "table_id": ARTICLE_TABLE_ID,
        "title_field": "文章主题",
    },
    "assets": {
        "base_token": ASSET_BASE_TOKEN,
        "table_id": ASSET_TABLE_ID,
        "title_field": "文章标题",
    },
}


def run_json(cmd: list[str], *, input_text: str | None = None) -> dict[str, Any]:
    result = subprocess.run(cmd, input=input_text, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not return JSON: {' '.join(cmd)}\n{result.stdout}") from exc


def first_select(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    return "" if value is None else str(value)


def list_records(base_token: str, table_id: str, fields: list[str] | None = None, limit: int = 200) -> list[dict[str, Any]]:
    cmd = [
        "lark-cli",
        "base",
        "+record-list",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--limit",
        str(limit),
        "--format",
        "json",
    ]
    for field in fields or []:
        cmd.extend(["--field-id", field])
    data = run_json(cmd)["data"]
    rows: list[dict[str, Any]] = []
    for record_id, values in zip(data.get("record_id_list", []), data.get("data", [])):
        row = dict(zip(data["fields"], values))
        row["record_id"] = record_id
        rows.append(row)
    return rows


def nonempty(row: dict[str, Any], key: str) -> bool:
    value = row.get(key)
    return value not in (None, "", [])


def meaningful_value(value: Any) -> bool:
    if value in (None, "", []):
        return False
    if isinstance(value, list):
        return any(meaningful_value(item) for item in value)
    return True


def count_by(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        if nonempty(row, field):
            counter[first_select(row.get(field))] += 1
    return dict(counter)


def blank_records(table_key: str) -> list[str]:
    table = TABLES[table_key]
    rows = list_records(
        table["base_token"],
        table["table_id"],
        None,
    )
    return [
        row["record_id"]
        for row in rows
        if not any(meaningful_value(value) for key, value in row.items() if key != "record_id")
    ]


def delete_records(base_token: str, table_id: str, record_ids: list[str]) -> dict[str, Any]:
    if not record_ids:
        return {"ok": True, "deleted": 0}
    cmd = [
        "lark-cli",
        "base",
        "+record-delete",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--json",
        json.dumps({"record_id_list": record_ids}, ensure_ascii=False),
        "--yes",
    ]
    return run_json(cmd)


def cleanup_blanks(args: argparse.Namespace) -> dict[str, Any]:
    table_keys = ["topics", "articles", "assets"] if args.cleanup_blanks == "all" else [args.cleanup_blanks]
    result: dict[str, Any] = {"ok": True, "write": args.write, "tables": {}}
    for key in table_keys:
        table = TABLES[key]
        record_ids = blank_records(key)
        item: dict[str, Any] = {
            "base_token": table["base_token"],
            "table_id": table["table_id"],
            "blank_record_ids": record_ids,
            "blank_count": len(record_ids),
        }
        if args.write and record_ids:
            item["delete_result"] = delete_records(table["base_token"], table["table_id"], record_ids)
        result["tables"][key] = item
    return result


def audit() -> dict[str, Any]:
    topic_rows = list_records(
        TOPIC_BASE_TOKEN,
        TOPIC_TABLE_ID,
        ["选题标题", "采集日期", "处理状态", "评估结论", "推荐排序", "内容栏目"],
    )
    article_rows = list_records(
        ARTICLE_BASE_TOKEN,
        ARTICLE_TABLE_ID,
        ["文章主题", "内容栏目", "审稿状态", "事实核验状态", "投资部确认", "AI预审结论", "初稿生成状态", "合规结论", "送审判断", "初稿链接", "本文转化目标", "期望动作", "发布后跟进建议"],
    )
    asset_rows = list_records(
        ASSET_BASE_TOKEN,
        ASSET_TABLE_ID,
        ["文章标题", "发布日期", "公众号链接", "内容栏目", "阅读量", "复盘等级", "线索跟进状态"],
    )

    topics_with_title = [row for row in topic_rows if nonempty(row, "选题标题")]
    articles_with_title = [row for row in article_rows if nonempty(row, "文章主题")]
    assets_with_title = [row for row in asset_rows if nonempty(row, "文章标题")]
    blocked_articles = [
        {
            "record_id": row["record_id"],
            "文章主题": row.get("文章主题"),
            "内容栏目": first_select(row.get("内容栏目")),
            "审稿状态": first_select(row.get("审稿状态")),
            "事实核验状态": first_select(row.get("事实核验状态")),
            "投资部确认": first_select(row.get("投资部确认")),
            "AI预审结论": first_select(row.get("AI预审结论")),
            "初稿生成状态": first_select(row.get("初稿生成状态")),
            "合规结论": first_select(row.get("合规结论")),
            "送审判断": first_select(row.get("送审判断")),
            "有初稿链接": bool(row.get("初稿链接")),
            "有转化目标": bool(row.get("本文转化目标")),
            "有跟进建议": bool(row.get("发布后跟进建议")),
        }
        for row in articles_with_title
        if first_select(row.get("送审判断")) == "暂不送审"
        or first_select(row.get("投资部确认")) == "待确认"
        or first_select(row.get("事实核验状态")) in {"未核验", "部分核验", "有疑点"}
    ]

    return {
        "ok": True,
        "date": dt.date.today().isoformat(),
        "topics": {
            "total_rows": len(topic_rows),
            "nonempty": len(topics_with_title),
            "blank_rows": len(topic_rows) - len(topics_with_title),
            "by_status": count_by(topics_with_title, "处理状态"),
            "by_evaluation": count_by(topics_with_title, "评估结论"),
            "by_column": count_by(topics_with_title, "内容栏目"),
        },
        "articles": {
            "total_rows": len(article_rows),
            "nonempty": len(articles_with_title),
            "blank_rows": len(article_rows) - len(articles_with_title),
            "by_review_status": count_by(articles_with_title, "审稿状态"),
            "by_route": count_by(articles_with_title, "送审判断"),
            "by_column": count_by(articles_with_title, "内容栏目"),
            "with_conversion_target": sum(1 for row in articles_with_title if bool(row.get("本文转化目标"))),
            "with_follow_up_advice": sum(1 for row in articles_with_title if bool(row.get("发布后跟进建议"))),
            "blocked_or_waiting": blocked_articles[:10],
        },
        "assets": {
            "total_rows": len(asset_rows),
            "nonempty": len(assets_with_title),
            "blank_rows": len(asset_rows) - len(assets_with_title),
            "by_reuse_level": count_by(assets_with_title, "复盘等级"),
            "by_column": count_by(assets_with_title, "内容栏目"),
            "by_lead_status": count_by(assets_with_title, "线索跟进状态"),
        },
    }


STAGES: dict[str, list[str]] = {
    "approve": ["strategy", "precheck", "draft", "compliance", "route", "packet"],
    "daily": ["collect", "evaluate"],
    "article": ["package", "strategy", "precheck", "draft", "compliance", "route", "packet"],
    "review": ["strategy", "precheck", "draft", "compliance", "route", "packet"],
    "blocked": ["packet"],
    "publish": ["publish"],
    "full": ["collect", "evaluate", "package", "strategy", "precheck", "draft", "compliance", "route", "packet"],
}

SCRIPT_BY_STAGE = {
    "collect": "topic_collector.py",
    "evaluate": "topic_evaluator.py",
    "package": "topic_package_generator.py",
    "strategy": "article_strategy_card_generator.py",
    "precheck": "strategy_precheck.py",
    "draft": "article_draft_generator.py",
    "compliance": "compliance_reviewer.py",
    "route": "review_router.py",
    "packet": "confirmation_packet_generator.py",
    "publish": "publish_asset_registrar.py",
}


def stage_command(stage: str, args: argparse.Namespace, article_record_id: str) -> list[str]:
    cmd = [PYTHON, str(ROOT / SCRIPT_BY_STAGE[stage])]
    if args.write:
        cmd.append("--write")
    if stage == "collect":
        cmd.extend(["--limit", str(args.limit)])
    if stage == "evaluate":
        cmd.extend(["--top", str(args.top)])
    if stage == "draft" and (args.force_draft or not args.write):
        cmd.append("--force")
    if stage in {"strategy", "precheck", "draft", "compliance", "route", "packet"}:
        target_id = article_record_id or args.record_id
        if target_id:
            cmd.extend(["--record-id", target_id])
    if stage == "publish":
        target_id = article_record_id or args.record_id
        if target_id:
            cmd.extend(["--record-id", target_id])
        if args.publish_url:
            cmd.extend(["--url", args.publish_url])
        if args.published_date:
            cmd.extend(["--published-date", args.published_date])
        if args.read_count is not None:
            cmd.extend(["--read-count", str(args.read_count)])
        if args.project_leads:
            cmd.extend(["--project-leads", args.project_leads])
        if args.institution_leads:
            cmd.extend(["--institution-leads", args.institution_leads])
        if args.leadership_feedback:
            cmd.extend(["--leadership-feedback", args.leadership_feedback])
        if args.interaction:
            cmd.extend(["--interaction", args.interaction])
        if args.retrospective_notes:
            cmd.extend(["--notes", args.retrospective_notes])
        if args.allow_unapproved_publish:
            cmd.append("--allow-unapproved")
    return cmd


def run_stage(stage: str, args: argparse.Namespace, article_record_id: str) -> tuple[dict[str, Any], str]:
    cmd = stage_command(stage, args, article_record_id)
    started = time.time()
    try:
        data = run_json(cmd)
        status = "ok" if data.get("ok") else "error"
    except Exception as exc:
        return {
            "stage": stage,
            "status": "error",
            "duration_seconds": round(time.time() - started, 2),
            "error": str(exc),
        }, article_record_id

    if stage == "package" and args.write:
        article_record_id = data.get("article_record_id") or article_record_id
    return {
        "stage": stage,
        "status": status,
        "duration_seconds": round(time.time() - started, 2),
        "result": data,
    }, article_record_id


def write_article_patch(record_id: str, patch: dict[str, Any]) -> dict[str, Any]:
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
    return run_json(cmd)


def approval_step(args: argparse.Namespace) -> dict[str, Any]:
    if not args.record_id:
        return {
            "stage": "approve",
            "status": "error",
            "error": "approve mode requires --record-id",
        }
    patch = {
        "投资部确认": args.investment_confirm,
        "事实核验状态": args.fact_status,
    }
    if not args.write:
        return {
            "stage": "approve",
            "status": "ok",
            "dry_run": True,
            "record_id": args.record_id,
            "patch": patch,
        }
    data = write_article_patch(args.record_id, patch)
    return {
        "stage": "approve",
        "status": "ok" if data.get("ok") else "error",
        "record_id": args.record_id,
        "patch": patch,
        "result": data,
    }


def run_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    stages = STAGES[args.mode]
    article_record_id = args.record_id
    results: list[dict[str, Any]] = []
    if args.mode == "approve":
        approval = approval_step(args)
        results.append(approval)
        if approval["status"] == "ok" and not args.write:
            results.append(
                {
                    "stage": "dry_run_stop",
                    "status": "ok",
                    "message": "approve dry-run only previews the status patch; pass --write to apply it and continue the review pipeline.",
                }
            )
            return {
                "ok": True,
                "mode": args.mode,
                "write": args.write,
                "article_record_id": article_record_id,
                "stages": results,
            }
        if approval["status"] != "ok":
            return {
                "ok": False,
                "mode": args.mode,
                "write": args.write,
                "article_record_id": article_record_id,
                "stages": results,
            }
    for stage in stages:
        result, article_record_id = run_stage(stage, args, article_record_id)
        results.append(result)
        if result["status"] != "ok" and not args.continue_on_error:
            break
        if stage == "package" and not args.write and not article_record_id and not args.record_id:
            results.append(
                {
                    "stage": "dry_run_stop",
                    "status": "ok",
                    "message": "package dry-run does not create an article record; pass --write to continue on the new record, or pass --record-id to preview an existing record.",
                }
            )
            break
    return {
        "ok": all(item["status"] == "ok" for item in results),
        "mode": args.mode,
        "write": args.write,
        "article_record_id": article_record_id,
        "stages": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Zhuge Capital WeChat operation pipeline.")
    parser.add_argument("--mode", choices=sorted(STAGES), default="full", help="pipeline scope")
    parser.add_argument("--write", action="store_true", help="write changes to Feishu; default is dry-run")
    parser.add_argument("--audit", action="store_true", help="print current Base status and exit")
    parser.add_argument("--cleanup-blanks", choices=["topics", "articles", "assets", "all"], help="list or delete blank records; deletion requires --write")
    parser.add_argument("--record-id", default="", help="continue one specific article production record")
    parser.add_argument("--limit", type=int, default=8, help="topic collection limit")
    parser.add_argument("--top", type=int, default=3, help="number of topic recommendations")
    parser.add_argument("--force-draft", action="store_true", help="create a new draft even if a draft link exists")
    parser.add_argument("--continue-on-error", action="store_true", help="keep running later stages after an error")
    parser.add_argument("--investment-confirm", default="可写", help="approve mode value for 投资部确认")
    parser.add_argument("--fact-status", default="已核验", help="approve mode value for 事实核验状态")
    parser.add_argument("--publish-url", default="", help="published WeChat URL for publish mode")
    parser.add_argument("--published-date", default=dt.date.today().isoformat(), help="publish mode date, YYYY-MM-DD")
    parser.add_argument("--read-count", type=int, default=0, help="publish mode read count")
    parser.add_argument("--project-leads", default="", help="publish mode project-side leads")
    parser.add_argument("--institution-leads", default="", help="publish mode institution/cooperation leads")
    parser.add_argument("--leadership-feedback", default="", help="publish mode leader feedback")
    parser.add_argument("--interaction", default="", help="publish mode forwarding/comments/private messages")
    parser.add_argument("--retrospective-notes", default="", help="publish mode manual retrospective notes")
    parser.add_argument("--allow-unapproved-publish", action="store_true", help="allow publish registration despite route/compliance warnings")
    args = parser.parse_args()

    if args.audit:
        print(json.dumps(audit(), ensure_ascii=False, indent=2))
        return 0

    if args.cleanup_blanks:
        print(json.dumps(cleanup_blanks(args), ensure_ascii=False, indent=2))
        return 0

    result = run_pipeline(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
