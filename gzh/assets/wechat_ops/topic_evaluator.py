#!/usr/bin/env python3
"""Evaluate collected WeChat topic candidates and mark daily recommendations."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

from topic_collector import first_select, infer_content_column


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "sources.yml"

READ_FIELDS = [
    "选题标题",
    "采集日期",
    "处理状态",
    "来源名称",
    "来源可信等级",
    "行业方向",
    "内容栏目",
    "目标主线",
    "推荐指数",
    "合规风险",
    "是否需要投资部确认",
    "与诸葛资本相关度",
    "目标价值判断",
    "投资部确认原因",
    "自动推荐动作",
    "诸葛资本钩子",
]

WRITE_FIELDS = ["评估结论", "推荐排序", "推荐理由", "写作切入角度", "写前确认事项", "内容栏目"]


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def list_records(base_token: str, table_id: str, limit: int) -> list[dict[str, Any]]:
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
    for field in READ_FIELDS + WRITE_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    fields = data["fields"]
    records: list[dict[str, Any]] = []
    for record_id, row in zip(data.get("record_id_list", []), data.get("data", [])):
        records.append({"record_id": record_id, **dict(zip(fields, row))})
    return records


def number(value: Any, default: float = 0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_record(record: dict[str, Any]) -> float:
    title = record.get("选题标题") or ""
    if not title or title.startswith("【示例】"):
        return -100
    status = first_select(record.get("处理状态"))
    if status in {"已淘汰", "已发布", "已复盘", "已转生产表"}:
        return -90

    score = number(record.get("推荐指数"), 1)
    relevance = first_select(record.get("与诸葛资本相关度"))
    action = first_select(record.get("自动推荐动作"))
    risk = first_select(record.get("合规风险"))
    trust = first_select(record.get("来源可信等级"))
    target = first_select(record.get("目标主线"))
    industries = record.get("行业方向") if isinstance(record.get("行业方向"), list) else []

    score += {"高": 3, "中": 1.5, "低": -1, "不相关": -4}.get(relevance, 0)
    score += {"直接进资料包": 3, "先投资部确认": 1, "暂缓观察": -1, "建议淘汰": -4}.get(action, 0)
    score += {"低": 1, "中": -0.5, "高": -5, "不建议写": -8}.get(risk, 0)
    if trust.startswith("A"):
        score += 1
    if target in {"领导认可型", "项目方引流型", "投资机构合作型"}:
        score += 1
    if any(x in industries for x in ["AI算力中心", "硬科技", "先进制造", "低空经济", "生物医药", "电子信息", "微波射频"]):
        score += 1
    if any(term in title for term in ["通知", "实施意见", "行动方案", "管理办法", "统计分类", "政策"]):
        score += 2
    if "调研" in title and not any(term in title for term in ["成都", "四川", "武侯", "诸葛"]):
        score -= 3
    return score


def writing_angle(record: dict[str, Any]) -> str:
    target = first_select(record.get("目标主线"))
    industries = "、".join(record.get("行业方向") or [])
    column = first_select(record.get("内容栏目")) or infer_content_column(target, record.get("行业方向") or [])
    if target == "领导认可型":
        return f"栏目建议：{column}。建议按“政策要求—区域产业—国资基金功能—诸葛资本行动”的顺序写，突出服务区域发展和产业培育，避免空泛表态。关联方向：{industries}。"
    if target == "项目方引流型":
        return f"栏目建议：{column}。建议按“产业趋势—项目痛点—区域资源—资本协同—合作入口”的顺序写，让项目方看到诸葛资本懂产业、懂政策、能协同资源。关联方向：{industries}。"
    if target == "投资机构合作型":
        return f"栏目建议：{column}。建议按“行业变化—合规边界—区域项目触达—国资基金协同”的顺序写，释放合作姿态，但不涉及具体募资和收益承诺。关联方向：{industries}。"
    return f"栏目建议：{column}。建议先观察，不急着写成公众号文章。关联方向：{industries}。"


def confirm_items(record: dict[str, Any]) -> str:
    need = first_select(record.get("是否需要投资部确认"))
    risk = first_select(record.get("合规风险"))
    reason = record.get("投资部确认原因") or ""
    items = ["核验原文链接、发布时间、发布机关，确认引用口径准确。"]
    if need == "是":
        items.append(reason or "请投资部确认该选题是否符合公司真实业务关注边界。")
    if risk in {"中", "高", "不建议写"}:
        items.append("涉及基金业务、监管或公开宣传边界，建议风控合规再看一遍。")
    return "；".join(item.rstrip("。") for item in items) + "。"


def recommendation_reason(record: dict[str, Any], rank: int, conclusion: str, score: float) -> str:
    target = first_select(record.get("目标主线"))
    relevance = first_select(record.get("与诸葛资本相关度"))
    value = record.get("目标价值判断") or ""
    action = first_select(record.get("自动推荐动作"))
    return f"排序第{rank}，评估分{score:.1f}。相关度：{relevance}；主线：{target}；系统动作：{action}。{value}"


def evaluate(records: list[dict[str, Any]], top: int) -> list[dict[str, Any]]:
    scored = [(score_record(r), r) for r in records]
    scored.sort(key=lambda item: item[0], reverse=True)
    rank = 0
    evaluated: list[dict[str, Any]] = []
    for score, record in scored:
        title = record.get("选题标题") or ""
        if not title:
            continue
        if score < -50:
            conclusion = "淘汰"
            sort_no = None
        else:
            rank += 1
            sort_no = rank
            if rank == 1 and score >= 8:
                conclusion = "今日强推"
            elif rank <= top and score >= 6:
                conclusion = "可备选"
            else:
                conclusion = "暂缓"
        evaluated.append(
            {
                "record_id": record["record_id"],
                "title": title,
                "score": score,
                "patch": {
                    "内容栏目": first_select(record.get("内容栏目")) or infer_content_column(
                        first_select(record.get("目标主线")),
                        record.get("行业方向") if isinstance(record.get("行业方向"), list) else [],
                    ),
                    "评估结论": conclusion,
                    "推荐排序": sort_no,
                    "推荐理由": recommendation_reason(record, sort_no or 0, conclusion, score),
                    "写作切入角度": writing_angle(record),
                    "写前确认事项": confirm_items(record),
                },
            }
        )
    return evaluated


def write_patch(base_token: str, table_id: str, record_id: str, patch: dict[str, Any]) -> None:
    cmd = [
        "lark-cli",
        "base",
        "+record-upsert",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--record-id",
        record_id,
        "--json",
        json.dumps(patch, ensure_ascii=False),
    ]
    run_lark_json(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Zhuge Capital WeChat topic candidates.")
    parser.add_argument("--write", action="store_true", help="write evaluation fields into Feishu Base")
    parser.add_argument("--top", type=int, default=3, help="number of recommended topics")
    parser.add_argument("--limit", type=int, default=100, help="max records to read from Feishu")
    args = parser.parse_args()

    config = load_config()
    base = config["feishu_base"]
    records = list_records(base["base_token"], base["table_id"], args.limit)
    evaluated = evaluate(records, args.top)
    report = {
        "ok": True,
        "date": dt.date.today().isoformat(),
        "recommendations": [
            {
                "record_id": item["record_id"],
                "title": item["title"],
                "score": round(item["score"], 1),
                **item["patch"],
            }
            for item in evaluated
            if item["patch"]["评估结论"] in {"今日强推", "可备选"}
        ],
    }

    if not args.write:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    for item in evaluated:
        write_patch(base["base_token"], base["table_id"], item["record_id"], item["patch"])
        time.sleep(0.6)
    report["written"] = len(evaluated)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
