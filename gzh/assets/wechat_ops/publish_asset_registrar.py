#!/usr/bin/env python3
"""Register a published WeChat article into the review and asset table."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from typing import Any


ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
ASSET_BASE_TOKEN = "LcazbM9W6aA8i8sb57Bcl4Xanog"
ASSET_TABLE_ID = "tbl5wvjIo8ifQx8s"

ARTICLE_FIELDS = [
    "文章主题",
    "内容栏目",
    "服务主线",
    "核心观点",
    "资料包摘要",
    "来源材料链接",
    "初稿链接",
    "本文转化目标",
    "期望动作",
    "发布后跟进建议",
    "审稿状态",
    "合规结论",
    "送审判断",
    "审稿意见/复盘结论",
]

ASSET_FIELDS = [
    "文章标题",
    "公众号链接",
    "复用摘要",
]


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def first_select(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    return "" if value is None else str(value)


def get_article(record_id: str) -> dict[str, Any]:
    cmd = [
        "lark-cli",
        "base",
        "+record-list",
        "--as",
        "user",
        "--base-token",
        ARTICLE_BASE_TOKEN,
        "--table-id",
        ARTICLE_TABLE_ID,
        "--limit",
        "100",
        "--format",
        "json",
    ]
    for field in ARTICLE_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    for row_id, values in zip(data.get("record_id_list", []), data.get("data", [])):
        if row_id == record_id:
            row = dict(zip(data["fields"], values))
            row["record_id"] = row_id
            return row
    raise RuntimeError(f"未找到文章生产记录：{record_id}")


def date_value(value: str) -> str:
    raw = value or dt.date.today().isoformat()
    try:
        parsed = dt.date.fromisoformat(raw)
    except ValueError as exc:
        raise RuntimeError("--published-date 必须使用 YYYY-MM-DD 格式") from exc
    return f"{parsed.isoformat()} 00:00:00"


def reuse_assets(column: str, content_type: str) -> list[str]:
    if column == "项目方指南" or content_type == "项目方引流型":
        return ["项目方沟通", "朋友圈转发"]
    if column == "机构合作观察" or content_type == "投资机构合作型":
        return ["机构合作", "朋友圈转发"]
    if column == "区域产业生态" or content_type == "领导认可型":
        return ["汇报素材", "朋友圈转发"]
    return ["汇报素材", "内部培训", "朋友圈转发"]


def infer_reuse_level(read_count: int, has_leads: bool, route: str) -> str:
    if read_count >= 1000 or has_leads:
        return "优秀"
    if route == "可送部长审":
        return "可复用"
    return "一般"


def infer_lead_status(args: argparse.Namespace) -> str:
    if args.lead_status:
        return args.lead_status
    has_leads = any([args.project_leads, args.institution_leads, args.leadership_feedback])
    return "待跟进" if has_leads else "无线索"


def build_reuse_summary(article: dict[str, Any], args: argparse.Namespace) -> str:
    parts = [
        f"来源生产记录：{article['record_id']}",
        f"内容栏目：{first_select(article.get('内容栏目')) or '未标注'}",
        f"转化目标：{article.get('本文转化目标') or '未填写'}",
        f"期望动作：{article.get('期望动作') or '未填写'}",
    ]
    if article.get("核心观点"):
        parts.append(f"核心观点：{article['核心观点']}")
    if article.get("初稿链接"):
        parts.append(f"初稿链接：{article['初稿链接']}")
    if args.notes:
        parts.append(f"人工复盘补充：{args.notes}")
    return "\n".join(parts)


def build_next_action(article: dict[str, Any], args: argparse.Namespace, lead_status: str) -> str:
    base = article.get("发布后跟进建议") or "发布后记录阅读、转发、留言、项目方和机构反馈，并在 7 天内判断是否需要转业务跟进。"
    if lead_status in {"待跟进", "跟进中"}:
        return f"{base}\n当前已有线索，建议明确责任人，3 个工作日内完成初步沟通并判断是否转投资部、招商或机构合作对接。"
    return base


def build_asset_record(article: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    column = first_select(article.get("内容栏目"))
    content_type = first_select(article.get("服务主线"))
    route = first_select(article.get("送审判断"))
    has_leads = any([args.project_leads, args.institution_leads, args.leadership_feedback])
    lead_status = infer_lead_status(args)
    record = {
        "文章标题": args.title or article.get("文章主题"),
        "发布日期": date_value(args.published_date),
        "公众号链接": args.url or "",
        "内容栏目": column,
        "内容类型": content_type,
        "阅读量": args.read_count,
        "复盘等级": args.reuse_level or infer_reuse_level(args.read_count, has_leads, route),
        "可复用资产": reuse_assets(column, content_type),
        "复用摘要": build_reuse_summary(article, args),
        "转发/互动情况": args.interaction or "待发布后补充阅读、转发、留言、朋友圈反馈和外部咨询情况。",
        "项目线索": args.project_leads or "",
        "机构合作线索": args.institution_leads or "",
        "领导反馈": args.leadership_feedback or "",
        "线索跟进状态": lead_status,
        "下一步动作": build_next_action(article, args, lead_status),
    }
    return {key: value for key, value in record.items() if value not in (None, "", [])}


def validate_publish(article: dict[str, Any], args: argparse.Namespace) -> list[str]:
    warnings: list[str] = []
    if not args.url:
        warnings.append("未提供公众号链接；dry-run 可预览，但 --write 时必须提供 --url。")
    if first_select(article.get("送审判断")) != "可送部长审":
        warnings.append("送审判断不是“可送部长审”，正式登记前需确认已经完成部长审/终审。")
    if first_select(article.get("合规结论")) not in {"能发", "修改后可发"}:
        warnings.append("合规结论不是“能发/修改后可发”，正式登记前需人工复核。")
    return warnings


def find_existing_asset_record(article: dict[str, Any], args: argparse.Namespace) -> str:
    cmd = [
        "lark-cli",
        "base",
        "+record-list",
        "--as",
        "user",
        "--base-token",
        ASSET_BASE_TOKEN,
        "--table-id",
        ASSET_TABLE_ID,
        "--limit",
        "100",
        "--format",
        "json",
    ]
    for field in ASSET_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    for row_id, values in zip(data.get("record_id_list", []), data.get("data", [])):
        row = dict(zip(data["fields"], values))
        summary = row.get("复用摘要") or ""
        url = row.get("公众号链接") or ""
        if article["record_id"] in summary or (args.url and args.url == url):
            return row_id
    return ""


def upsert_asset_record(record: dict[str, Any], existing_record_id: str = "") -> dict[str, Any]:
    cmd = [
        "lark-cli",
        "base",
        "+record-upsert",
        "--as",
        "user",
        "--base-token",
        ASSET_BASE_TOKEN,
        "--table-id",
        ASSET_TABLE_ID,
    ]
    if existing_record_id:
        cmd.extend(["--record-id", existing_record_id])
    cmd.extend(["--json", json.dumps(record, ensure_ascii=False)])
    return run_lark_json(cmd)


def update_article_published(article: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    previous_note = article.get("审稿意见/复盘结论") or ""
    publish_note = f"已登记发布复盘：{args.url}；发布日期：{args.published_date or dt.date.today().isoformat()}"
    patch = {
        "审稿状态": "已发布",
        "审稿意见/复盘结论": f"{previous_note}\n{publish_note}".strip(),
    }
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
        article["record_id"],
        "--json",
        json.dumps(patch, ensure_ascii=False),
    ]
    return run_lark_json(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a published article into the asset review table.")
    parser.add_argument("--record-id", required=True, help="03 单篇文章生产表 record_id")
    parser.add_argument("--url", default="", help="published WeChat article URL")
    parser.add_argument("--title", default="", help="override published title")
    parser.add_argument("--published-date", default=dt.date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--read-count", type=int, default=0)
    parser.add_argument("--reuse-level", choices=["优秀", "可复用", "一般", "不建议复用"], default="")
    parser.add_argument("--lead-status", choices=["无线索", "待跟进", "跟进中", "已转业务", "暂不跟进"], default="")
    parser.add_argument("--project-leads", default="", help="project-side leads after publication")
    parser.add_argument("--institution-leads", default="", help="institution/cooperation leads after publication")
    parser.add_argument("--leadership-feedback", default="", help="leader or SOE-system feedback")
    parser.add_argument("--interaction", default="", help="forwarding, comments, private messages, or other interactions")
    parser.add_argument("--notes", default="", help="manual retrospective notes")
    parser.add_argument("--write", action="store_true", help="write asset record and mark source article as published")
    parser.add_argument("--allow-unapproved", action="store_true", help="allow write even when route/compliance warnings exist")
    args = parser.parse_args()

    article = get_article(args.record_id)
    warnings = validate_publish(article, args)
    if args.write and not args.url:
        raise RuntimeError("--write 登记发布复盘时必须提供 --url")
    blocking_warnings = [item for item in warnings if not item.startswith("未提供公众号链接")]
    if args.write and blocking_warnings and not args.allow_unapproved:
        print(
            json.dumps(
                {
                    "ok": False,
                    "dry_run": False,
                    "record_id": args.record_id,
                    "warnings": warnings,
                    "message": "存在发布前合规/送审提醒；确认已完成人工审批后，可加 --allow-unapproved 写入。",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    asset_record = build_asset_record(article, args)
    existing_asset_record_id = find_existing_asset_record(article, args)
    result: dict[str, Any] = {
        "ok": True,
        "dry_run": not args.write,
        "record_id": args.record_id,
        "article": article.get("文章主题"),
        "warnings": warnings,
        "existing_asset_record_id": existing_asset_record_id,
        "asset_record": asset_record,
    }
    if args.write:
        result["asset_result"] = upsert_asset_record(asset_record, existing_asset_record_id)
        result["article_result"] = update_article_published(article, args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
