#!/usr/bin/env python3
"""Collect public topic candidates for Zhuge Capital WeChat operations."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "sources.yml"
STATE_PATH = ROOT / "state" / "seen_urls.json"


INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "生物医药": ["生物医药", "医药", "医疗器械", "转化医学", "新药", "大健康", "医疗卫生"],
    "电子信息": ["电子信息", "集成电路", "信息通信", "软件", "工业互联网", "数字经济"],
    "微波射频": ["微波射频", "射频", "通信模组", "雷达"],
    "AI算力中心": ["人工智能", "AI", "算力", "智算", "数据中心", "大模型"],
    "硬科技": ["硬科技", "科技创新", "新质生产力", "专精特新", "科创", "成果转化"],
    "先进制造": ["先进制造", "制造业", "新型工业化", "机器人", "设备更新", "智能制造"],
    "低空经济": ["低空经济", "低空", "无人机", "通用航空", "低空基础设施"],
    "文旅消费": ["文旅", "消费", "商务服务", "服务业", "商贸", "平台经济"],
    "政策/国资": ["国资", "国有企业", "政府引导基金", "私募股权", "基金", "资本市场", "政策"],
}

COMPLIANCE_TERMS = ["私募", "基金", "募集", "投资者", "信息披露", "收益", "承诺", "保本", "监管"]
IMPORTANT_TERMS = [
    "人工智能",
    "算力",
    "低空经济",
    "先进制造",
    "生物医药",
    "电子信息",
    "微波射频",
    "新质生产力",
    "国资",
    "私募",
    "股权",
    "基金",
    "资本市场",
    "科技创新",
    "成果转化",
    "服务业",
    "文旅",
    "消费",
]


@dataclass
class Candidate:
    title: str
    url: str
    source_name: str
    source_type: str
    trust_level: str
    published: str | None = None
    summary: str = ""

    @property
    def key(self) -> str:
        raw = self.url or self.title
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_seen() -> set[str]:
    if not STATE_PATH.exists():
        return set()
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return set(json.load(f))


def save_seen(seen: set[str]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def fetch_html(url: str, timeout: int = 18) -> str:
    headers = {"User-Agent": "Mozilla/5.0 ZhugeTopicCollector/0.1"}
    r = requests.get(url, timeout=timeout, headers=headers)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() in {"iso-8859-1", "ascii"}:
        r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def likely_content_link(title: str, href: str) -> bool:
    if not title or len(title) < 8:
        return False
    if href.startswith(("javascript:", "#", "mailto:")):
        return False
    blocked = ["English", "ICP备", "公网安备", "网站地图", "联系我们", "无障碍", "登录", "首页"]
    return not any(x in title for x in blocked)


def parse_list_page(source: dict[str, Any]) -> list[Candidate]:
    candidates: list[Candidate] = []
    base_url = source["url"]
    try:
        html = fetch_html(base_url)
    except Exception as exc:
        print(f"[warn] failed source {source['name']}: {exc}", file=sys.stderr)
        return candidates

    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a"):
        title = clean_text(a.get_text(" ", strip=True))
        href = a.get("href") or ""
        if not likely_content_link(title, href):
            continue
        url = urljoin(base_url, href)
        if urlparse(url).netloc and source.get("domain") not in urlparse(url).netloc:
            continue
        candidates.append(
            Candidate(
                title=title,
                url=url,
                source_name=source["name"],
                source_type=source["source_type"],
                trust_level=source["trust_level"],
            )
        )
    return candidates


def load_seed_items(config: dict[str, Any]) -> list[Candidate]:
    items: list[Candidate] = []
    for item in config.get("seed_items", []):
        items.append(
            Candidate(
                title=item["title"],
                url=item["url"],
                source_name=item["source_name"],
                source_type=item["source_type"],
                trust_level=item["trust_level"],
                published=item.get("published"),
                summary=item.get("summary", ""),
            )
        )
    return items


def infer_industries(text: str) -> list[str]:
    hits: list[str] = []
    for industry, terms in INDUSTRY_KEYWORDS.items():
        if any(term.lower() in text.lower() for term in terms):
            hits.append(industry)
    return hits or ["其他"]


def infer_target_line(text: str, source_type: str, industries: list[str]) -> str:
    lower = text.lower()
    if any(term in text for term in ["私募", "基金", "资本市场", "监管", "信息披露", "证券"]):
        return "投资机构合作型"
    if any(x in industries for x in ["AI算力中心", "生物医药", "电子信息", "微波射频", "低空经济", "先进制造", "文旅消费"]):
        return "项目方引流型"
    if source_type == "官方政策源" or any(term in lower for term in ["gov", "政策", "国资"]):
        return "领导认可型"
    return "暂不适合"


def infer_content_column(target_line: str, industries: list[str]) -> str:
    if target_line == "投资机构合作型":
        return "机构合作观察"
    if target_line == "项目方引流型":
        return "项目方指南"
    if target_line == "领导认可型" or "政策/国资" in industries:
        return "区域产业生态"
    return "产业观察"


def compliance_risk(text: str, target_line: str) -> str:
    hits = sum(1 for term in COMPLIANCE_TERMS if term in text)
    if "收益" in text or "承诺" in text or "保本" in text:
        return "高"
    if target_line == "投资机构合作型" or hits >= 2:
        return "中"
    return "低"


def needs_investment_confirm(target_line: str, industries: list[str], risk: str) -> str:
    if risk in {"中", "高"}:
        return "是"
    if target_line in {"项目方引流型", "投资机构合作型"}:
        return "是"
    if any(x in industries for x in ["AI算力中心", "生物医药", "电子信息", "微波射频", "低空经济", "先进制造"]):
        return "是"
    return "否"


def judge_relevance(industries: list[str], target_line: str, trust_level: str, text: str) -> str:
    if target_line == "暂不适合" or industries == ["其他"]:
        return "低"
    core_industries = {
        "生物医药",
        "电子信息",
        "微波射频",
        "AI算力中心",
        "硬科技",
        "先进制造",
        "低空经济",
        "政策/国资",
    }
    if any(industry in core_industries for industry in industries):
        return "高"
    if trust_level.startswith("A") and any(term in text for term in IMPORTANT_TERMS):
        return "中"
    return "低"


def target_value_judgement(target_line: str, industries: list[str], risk: str) -> str:
    industry_text = "、".join(industries)
    leader = "中"
    project = "低"
    institution = "低"
    if target_line == "领导认可型" or "政策/国资" in industries:
        leader = "高"
    if any(x in industries for x in ["生物医药", "电子信息", "微波射频", "AI算力中心", "硬科技", "先进制造", "低空经济", "文旅消费"]):
        project = "高"
    if target_line == "投资机构合作型" or risk in {"中", "高"} or "政策/国资" in industries:
        institution = "中" if institution == "低" else institution
    if target_line == "投资机构合作型":
        institution = "高"
    return f"领导认可：{leader}；项目方引流：{project}；机构合作：{institution}。建议主打：{target_line}。关联方向：{industry_text}。"


def investment_confirmation_reason(confirm: str, target_line: str, industries: list[str], risk: str) -> str:
    if confirm == "否":
        return "暂不需要投资部确认：主要是官方政策或宏观趋势选题，不直接涉及公司项目事实、投资判断或具体合作承诺。"
    reasons: list[str] = []
    if target_line == "项目方引流型":
        reasons.append("涉及产业判断和项目方吸引口径")
    if target_line == "投资机构合作型":
        reasons.append("涉及基金业务、机构合作或监管边界")
    if risk in {"中", "高"}:
        reasons.append(f"合规风险初判为{risk}")
    if any(x in industries for x in ["AI算力中心", "生物医药", "电子信息", "微波射频", "低空经济", "先进制造"]):
        reasons.append("涉及公司重点产业方向，需要确认是否符合真实投资关注边界")
    return "需要投资部确认：" + "；".join(dict.fromkeys(reasons)) + "。"


def recommended_action(relevance: str, score: int, confirm: str, risk: str) -> str:
    if relevance == "不相关" or score <= 2:
        return "建议淘汰"
    if risk == "高":
        return "暂缓观察"
    if confirm == "是":
        return "先投资部确认"
    if relevance in {"高", "中"} and score >= 4:
        return "直接进资料包"
    return "暂缓观察"


def score_candidate(text: str, industries: list[str], target_line: str, trust_level: str) -> int:
    score = 1
    score += min(2, sum(1 for term in IMPORTANT_TERMS if term in text) // 2)
    if trust_level.startswith("A"):
        score += 1
    if target_line != "暂不适合":
        score += 1
    if "其他" not in industries:
        score += 1
    return max(1, min(5, score))


def make_summary(candidate: Candidate, industries: list[str], target_line: str, risk: str) -> tuple[str, str, str]:
    title = candidate.title
    industry_text = "、".join(industries)
    summary = candidate.summary or f"公开来源显示，该信息与{industry_text}相关，可作为公众号选题线索。"
    if target_line == "领导认可型":
        hook = "可从政策导向、区域产业培育、国资基金功能三个角度写，重点证明诸葛资本服务区域发展和产业升级。"
    elif target_line == "项目方引流型":
        hook = "可从产业趋势、区域资源、资本协同和场景落地角度写，吸引相关项目方关注诸葛资本。"
    elif target_line == "投资机构合作型":
        hook = "可从合规意识、区域项目触达、产业资源协同和长期合作机制角度写，吸引投资机构与专业服务机构合作。"
    else:
        hook = "暂时只作为线索保留，需人工判断是否和诸葛资本公众号目标相关。"
    note = f"自动采集生成，正式写稿前请核验原文。合规风险初判：{risk}。原始标题：{title}"
    return summary, hook, note


def build_record(candidate: Candidate, today: str) -> dict[str, Any]:
    text = f"{candidate.title} {candidate.summary}"
    industries = infer_industries(text)
    target_line = infer_target_line(text, candidate.source_type, industries)
    risk = compliance_risk(text, target_line)
    confirm = needs_investment_confirm(target_line, industries, risk)
    score = score_candidate(text, industries, target_line, candidate.trust_level)
    relevance = judge_relevance(industries, target_line, candidate.trust_level, text)
    value_judgement = target_value_judgement(target_line, industries, risk)
    confirm_reason = investment_confirmation_reason(confirm, target_line, industries, risk)
    action = recommended_action(relevance, score, confirm, risk)
    if action == "建议淘汰":
        status = "已淘汰"
    elif action == "先投资部确认":
        status = "待投资部确认"
    else:
        status = "可深入"
    summary, hook, note = make_summary(candidate, industries, target_line, risk)
    return {
        "选题标题": candidate.title,
        "采集日期": f"{today} 00:00:00",
        "处理状态": status,
        "来源链接": candidate.url,
        "来源名称": candidate.source_name,
        "来源类型": candidate.source_type,
        "来源可信等级": candidate.trust_level,
        "行业方向": industries,
        "内容栏目": infer_content_column(target_line, industries),
        "目标主线": target_line,
        "内容摘要": summary,
        "诸葛资本钩子": hook,
        "推荐指数": score,
        "合规风险": risk,
        "是否需要投资部确认": confirm,
        "与诸葛资本相关度": relevance,
        "目标价值判断": value_judgement,
        "投资部确认原因": confirm_reason,
        "自动推荐动作": action,
        "备注/下一步": note,
    }


def collect(config: dict[str, Any]) -> list[Candidate]:
    candidates = load_seed_items(config)
    for source in config.get("sources", []):
        candidates.extend(parse_list_page(source))

    deduped: dict[str, Candidate] = {}
    for item in candidates:
        text = f"{item.title} {item.summary}"
        if not any(term in text for term in IMPORTANT_TERMS):
            continue
        deduped.setdefault(item.key, item)
    return list(deduped.values())


def write_record(record: dict[str, Any], base_token: str, table_id: str) -> str:
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
        "--json",
        json.dumps(record, ensure_ascii=False),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    data = json.loads(result.stdout)
    record_ids = data.get("data", {}).get("record", {}).get("record_id_list", [])
    return record_ids[0] if record_ids else ""


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def first_select(value: Any, default: str = "") -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    if value is None:
        return default
    return str(value)


def list_existing_records(base_token: str, table_id: str) -> list[dict[str, Any]]:
    fields = [
        "选题标题",
        "内容摘要",
        "来源类型",
        "来源可信等级",
        "行业方向",
        "内容栏目",
        "目标主线",
        "合规风险",
        "推荐指数",
        "是否需要投资部确认",
        "与诸葛资本相关度",
    ]
    offset = 0
    rows: list[dict[str, Any]] = []
    while True:
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
            "100",
            "--offset",
            str(offset),
            "--format",
            "json",
        ]
        for field in fields:
            cmd.extend(["--field-id", field])
        data = run_lark_json(cmd)["data"]
        for record_id, row in zip(data.get("record_id_list", []), data.get("data", [])):
            rows.append({"record_id": record_id, **dict(zip(fields, row))})
        if not data.get("has_more"):
            break
        offset += 100
    return rows


def backfill_existing_records(base_token: str, table_id: str, force: bool = False) -> list[dict[str, str]]:
    updated: list[dict[str, str]] = []
    for row in list_existing_records(base_token, table_id):
        title = row.get("选题标题")
        if not title:
            continue
        if row.get("与诸葛资本相关度") and not force:
            continue
        summary = row.get("内容摘要") or ""
        text = f"{title} {summary}"
        industries = row.get("行业方向") if isinstance(row.get("行业方向"), list) else infer_industries(text)
        target_line = first_select(row.get("目标主线")) or infer_target_line(text, first_select(row.get("来源类型")), industries)
        risk = first_select(row.get("合规风险")) or compliance_risk(text, target_line)
        confirm = first_select(row.get("是否需要投资部确认")) or needs_investment_confirm(target_line, industries, risk)
        trust_level = first_select(row.get("来源可信等级"), "A 原始/官方")
        score = int(row.get("推荐指数") or score_candidate(text, industries, target_line, trust_level))
        relevance = judge_relevance(industries, target_line, trust_level, text)
        patch = {
            "内容栏目": first_select(row.get("内容栏目")) or infer_content_column(target_line, industries),
            "与诸葛资本相关度": relevance,
            "目标价值判断": target_value_judgement(target_line, industries, risk),
            "投资部确认原因": investment_confirmation_reason(confirm, target_line, industries, risk),
            "自动推荐动作": recommended_action(relevance, score, confirm, risk),
        }
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
            row["record_id"],
            "--json",
            json.dumps(patch, ensure_ascii=False),
        ]
        run_lark_json(cmd)
        updated.append({"record_id": row["record_id"], "title": title})
        time.sleep(0.8)
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Zhuge Capital WeChat topic candidates.")
    parser.add_argument("--write", action="store_true", help="write records into Feishu Base")
    parser.add_argument("--backfill", action="store_true", help="backfill decision fields for existing Feishu records")
    parser.add_argument("--force-backfill", action="store_true", help="overwrite existing decision fields during backfill")
    parser.add_argument("--limit", type=int, default=8, help="max records to output/write")
    parser.add_argument("--ignore-state", action="store_true", help="ignore local seen URL state")
    args = parser.parse_args()

    config = load_config()
    base = config["feishu_base"]
    if args.backfill:
        updated = backfill_existing_records(base["base_token"], base["table_id"], force=args.force_backfill)
        print(json.dumps({"ok": True, "backfilled": updated}, ensure_ascii=False, indent=2))
        return 0

    today = dt.date.today().isoformat()
    seen = set() if args.ignore_state else load_seen()
    candidates = [c for c in collect(config) if c.key not in seen]
    records = [build_record(c, today) for c in candidates]
    records.sort(key=lambda r: (r["推荐指数"], r["合规风险"] == "低"), reverse=True)
    records = records[: args.limit]

    if not records:
        print(json.dumps({"ok": True, "records": [], "message": "no new candidates"}, ensure_ascii=False, indent=2))
        return 0

    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "records": records}, ensure_ascii=False, indent=2))
        return 0

    written: list[dict[str, str]] = []
    key_by_url = {c.url: c.key for c in candidates}
    for record in records:
        record_id = write_record(record, base["base_token"], base["table_id"])
        written.append({"record_id": record_id, "title": record["选题标题"]})
        seen.add(key_by_url.get(record["来源链接"], hashlib.sha1(record["来源链接"].encode("utf-8")).hexdigest()))
        time.sleep(0.8)
    save_seen(seen)
    print(json.dumps({"ok": True, "written": written}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
