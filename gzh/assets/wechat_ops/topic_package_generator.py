#!/usr/bin/env python3
"""Generate an article material package from the top recommended topic."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml
from bs4 import BeautifulSoup

from topic_collector import first_select, infer_content_column


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "sources.yml"
POLICY_INDEX = ROOT.parent / "policies" / "index.json"
POLICY_80_INDEX = ROOT.parent / "policies" / "80条政策_索引.json"

TOPIC_BASE_TOKEN = "FUreb5ROTaYkoHsciK3c5h3unpP"
TOPIC_TABLE_ID = "tblyhgqm9SKvxMup"
TODAY_RECOMMEND_VIEW_ID = "vewEIY81d6"

ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"

TOPIC_FIELDS = [
    "选题标题",
    "来源链接",
    "来源名称",
    "处理状态",
    "行业方向",
    "内容栏目",
    "目标主线",
    "内容摘要",
    "诸葛资本钩子",
    "合规风险",
    "是否需要投资部确认",
    "投资部确认原因",
    "评估结论",
    "推荐排序",
    "推荐理由",
    "写作切入角度",
    "写前确认事项",
]


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_url(value: str) -> str:
    value = value or ""
    match = re.search(r"\((https?://[^)]+)\)", value)
    if match:
        return match.group(1)
    match = re.search(r"https?://\S+", value)
    return match.group(0).rstrip(")") if match else value


def fetch_article_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=18, headers={"User-Agent": "Mozilla/5.0 ZhugePackageGenerator/0.1"})
        r.raise_for_status()
        if not r.encoding or r.encoding.lower() in {"iso-8859-1", "ascii"}:
            r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        parts = [clean_text(p.get_text(" ", strip=True)) for p in soup.find_all(["h1", "h2", "p", "li"])]
        parts = [p for p in parts if len(p) >= 12]
        return "\n".join(parts[:40])
    except Exception as exc:
        return f"原文抓取失败：{exc}"


def get_top_topic() -> dict[str, Any]:
    cmd = [
        "lark-cli",
        "base",
        "+record-list",
        "--as",
        "user",
        "--base-token",
        TOPIC_BASE_TOKEN,
        "--table-id",
        TOPIC_TABLE_ID,
        "--limit",
        "100",
        "--format",
        "json",
    ]
    for field in TOPIC_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list"):
        raise RuntimeError("选题库没有可用记录")

    rows: list[dict[str, Any]] = []
    for record_id, values in zip(data.get("record_id_list", []), data.get("data", [])):
        row = dict(zip(data["fields"], values))
        row["record_id"] = record_id
        rows.append(row)

    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        conclusion = first_select(row.get("评估结论"))
        rank = row.get("推荐排序")
        try:
            rank_no = int(rank)
        except (TypeError, ValueError):
            rank_no = 999
        conclusion_score = {"今日强推": 0, "可备选": 1}.get(conclusion, 9)
        return (conclusion_score, rank_no, row.get("选题标题") or "")

    blocked_status = {"已淘汰", "已发布", "已复盘", "已转生产表"}
    candidates = [
        row
        for row in rows
        if row.get("选题标题")
        and not str(row.get("选题标题")).startswith("【示例】")
        and first_select(row.get("处理状态")) not in blocked_status
        and first_select(row.get("评估结论")) in {"今日强推", "可备选"}
    ]
    if not candidates:
        raise RuntimeError("没有可转入生产表的今日推荐选题；请先运行 topic_evaluator.py --write 或调整选题状态")
    return sorted(candidates, key=sort_key)[0]


def policy_matches(industries: list[str]) -> list[str]:
    policy_index = load_json(POLICY_INDEX)
    policy_80 = load_json(POLICY_80_INDEX)
    matches: list[str] = []
    aliases = {
        "AI算力中心": ["AI算力中心", "人工智能", "机器人", "互联网", "软件", "数字经济"],
        "硬科技": ["硬科技", "科技创新", "成果转化", "高新技术"],
        "先进制造": ["先进制造", "智能制造", "工业", "制造业", "设备更新"],
        "低空经济": ["低空经济", "低空"],
        "生物医药": ["生物医药", "大健康", "转化医学", "新药", "医疗器械"],
        "电子信息": ["电子信息", "信息通信", "软件", "互联网"],
    }
    terms = set(industries)
    for industry in industries:
        terms.update(aliases.get(industry, []))
    for doc in policy_index.get("documents", []):
        scenarios = "、".join(doc.get("scenarios", []))
        key_points = "；".join(doc.get("key_points", [])[:3])
        text = f"{doc.get('name', '')} {scenarios} {key_points}"
        if any(term in text for term in terms):
            matches.append(f"{doc.get('name')}：{key_points}")
    quick = policy_80.get("quick_match", {})
    for industry in industries:
        for key, nums in quick.items():
            if industry in key or key in industry or any(term in key for term in aliases.get(industry, [])):
                matches.append(f"武侯区产业政策 80 条：{key} 对应条款 {nums}")
    return matches[:5]


def target_readers(target_line: str) -> list[str]:
    if target_line == "领导认可型":
        return ["区委区政府/国资系统"]
    if target_line == "项目方引流型":
        return ["项目方", "投资机构"]
    if target_line == "投资机构合作型":
        return ["投资机构", "合作机构"]
    return ["内部员工"]


def content_column(topic: dict[str, Any], target: str, industries: list[str]) -> str:
    return first_select(topic.get("内容栏目")) or infer_content_column(target, industries)


def conversion_target(column: str, target: str) -> str:
    if column == "项目方指南" or target == "项目方引流型":
        return "让相关项目方感到诸葛资本懂产业、懂政策、能协同区域资源，愿意在合规边界内发起产业交流或项目对接。"
    if column == "机构合作观察" or target == "投资机构合作型":
        return "让基金、券商、律所、会计师事务所、FA、产业投资部门看到诸葛资本的区域项目触达和协同价值，形成合作线索。"
    if column == "区域产业生态" or target == "领导认可型":
        return "沉淀可供领导认可、对上汇报和区域品牌展示的内容资产，体现国资基金服务产业培育的专业能力。"
    return "提升诸葛资本在重点产业方向上的专业品牌认知，沉淀可复用的产业观察素材。"


def expected_action(column: str, target: str) -> str:
    if column == "项目方指南" or target == "项目方引流型":
        return "项目方阅读后愿意咨询政策、载体、场景、资本协同或提交项目交流需求；综合部可转投资部或招商线索池。"
    if column == "机构合作观察" or target == "投资机构合作型":
        return "合作机构阅读后愿意提供项目线索、共研赛道、联合走访或建立常态化合作沟通。"
    if column == "区域产业生态" or target == "领导认可型":
        return "适合公司领导、国资系统和综合部转发，可作为汇报材料、品牌展示和区域产业推介素材。"
    return "适合内部学习、朋友圈转发和后续同类选题复用。"


def ending_entry(column: str, target: str) -> str:
    if column == "项目方指南" or target == "项目方引流型":
        return "欢迎相关项目方在合规边界内围绕产业落地、政策匹配、场景对接和资本协同开展交流；本文不构成投资承诺、基金推介或收益承诺。"
    if column == "机构合作观察" or target == "投资机构合作型":
        return "欢迎基金、券商、律所、会计师事务所、FA 及产业投资机构围绕项目线索、产业研究和区域协同开展交流；不涉及具体基金募集或收益承诺。"
    if column == "区域产业生态" or target == "领导认可型":
        return "诸葛资本将继续围绕区域产业发展，在合规、审慎、专业的前提下发挥国资基金平台作用，服务优质企业和产业生态建设。"
    return "欢迎相关主体在合规边界内开展产业交流，共同关注区域产业发展和企业成长机会。"


def follow_up_advice(column: str, target: str) -> str:
    if column == "项目方指南" or target == "项目方引流型":
        return "发布后 24 小时观察项目方咨询、朋友圈转发和留言；7 天内汇总可跟进项目线索，必要时转投资部或招商对接。"
    if column == "机构合作观察" or target == "投资机构合作型":
        return "发布后重点观察机构转发、私信、项目推荐和合作邀约；7 天内整理机构名单和可跟进事项。"
    if column == "区域产业生态" or target == "领导认可型":
        return "发布后关注领导反馈、国资系统转发和内部认可度；可沉淀为汇报素材、招商推介素材和公司品牌素材。"
    return "发布后记录阅读、转发和外部反馈，判断是否值得扩展为系列选题。"


def article_theme(topic: dict[str, Any], industries: list[str]) -> str:
    title = topic.get("选题标题") or ""
    if "人工智能" in title and "制造" in title:
        return "从“人工智能+制造”看国资基金如何服务硬科技企业成长"
    if "算力" in title:
        return "从国家算力互联互通看区域产业升级的新机会"
    if "低空" in title:
        return "从低空基础设施建设看区域产业生态的新空间"
    industry_text = "、".join(industries[:2])
    return f"从{industry_text or '产业政策'}看诸葛资本服务区域产业发展的发力点"


def core_viewpoint(topic: dict[str, Any], industries: list[str]) -> str:
    target = first_select(topic.get("目标主线"))
    business_industries = [x for x in industries if x != "政策/国资"]
    industry_text = "、".join(business_industries or industries)
    if target == "项目方引流型":
        return f"这篇文章不应只搬运政策，而要说明：{industry_text}相关企业成长需要政策、场景、资本、产业资源一起协同；诸葛资本的价值在于用国资基金工具连接区域资源和产业机会。"
    if target == "领导认可型":
        return f"这篇文章应证明诸葛资本能把上级政策要求转化为服务区域产业的具体动作，重点体现国企功能、产业培育和专业判断。关联方向：{industry_text}。"
    if target == "投资机构合作型":
        return f"这篇文章应释放合作信号：诸葛资本具备区域项目触达、产业场景和国资协同价值，但必须避免公开募资、收益承诺和具体基金产品推介。关联方向：{industry_text}。"
    return f"这篇文章需要先判断和诸葛资本目标的真实关系。关联方向：{industry_text}。"


def package_summary(topic: dict[str, Any], source_text: str, matched_policies: list[str]) -> str:
    title = topic.get("选题标题") or ""
    industries = topic.get("行业方向") or []
    target = first_select(topic.get("目标主线"))
    risk = first_select(topic.get("合规风险"))
    source_excerpt = clean_text(source_text.replace("\n", " "))[:500]
    policies = "；".join(matched_policies) if matched_policies else "暂未匹配到本地武侯政策条目，正式写稿时建议补充区域政策或公司内部材料。"
    return (
        f"【原始选题】{title}\n"
        f"【服务主线】{target}\n"
        f"【行业方向】{'、'.join(industries)}\n"
        f"【原文要点】{source_excerpt}\n"
        f"【本地政策/区域连接】{policies}\n"
        f"【诸葛资本角度】{topic.get('诸葛资本钩子') or ''}\n"
        f"【写作建议】{topic.get('写作切入角度') or ''}\n"
        f"【写前确认】{topic.get('写前确认事项') or ''}\n"
        f"【风险提醒】合规风险初判：{risk}。不得写成基金产品推介、公开募资、收益承诺或具体投资承诺；涉及公司真实投资关注边界时，需要投资部确认。"
    )


def build_article_record(topic: dict[str, Any]) -> dict[str, Any]:
    industries = topic.get("行业方向") if isinstance(topic.get("行业方向"), list) else []
    target = first_select(topic.get("目标主线"))
    column = content_column(topic, target, industries)
    url = normalize_url(topic.get("来源链接") or "")
    source_text = fetch_article_text(url) if url else ""
    matched_policies = policy_matches(industries)
    need_confirm = first_select(topic.get("是否需要投资部确认"))
    return {
        "文章主题": article_theme(topic, industries),
        "创建日期": f"{dt.date.today().isoformat()} 00:00:00",
        "内容栏目": column,
        "服务主线": target,
        "目标读者": target_readers(target),
        "核心观点": core_viewpoint(topic, industries),
        "来源材料链接": url,
        "资料包摘要": package_summary(topic, source_text, matched_policies),
        "事实核验状态": "部分核验" if source_text and not source_text.startswith("原文抓取失败") else "未核验",
        "投资部确认": "待确认" if need_confirm == "是" else "不需要",
        "合规结论": "未审查",
        "审稿状态": "待综合部初稿",
        "本文转化目标": conversion_target(column, target),
        "期望动作": expected_action(column, target),
        "文章结尾承接口径": ending_entry(column, target),
        "发布后跟进建议": follow_up_advice(column, target),
        "分发对象": "公众号主文；必要时可拆成投资机构合作转发话术、项目方沟通话术。",
        "承接动作": "先由投资部确认产业方向和公司关注边界；确认后进入文章策略卡和初稿生成。",
        "审稿意见/复盘结论": f"来源选题记录：{topic.get('record_id')}；评估结论：{first_select(topic.get('评估结论'))}；推荐排序：{topic.get('推荐排序')}",
    }


def create_article_record(record: dict[str, Any]) -> str:
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
        "--json",
        json.dumps(record, ensure_ascii=False),
    ]
    data = run_lark_json(cmd)["data"]
    record_ids = data.get("record", {}).get("record_id_list", [])
    return record_ids[0] if record_ids else ""


def update_topic_status(topic_record_id: str) -> None:
    patch = {"处理状态": "已转生产表"}
    cmd = [
        "lark-cli",
        "base",
        "+record-upsert",
        "--as",
        "user",
        "--base-token",
        TOPIC_BASE_TOKEN,
        "--table-id",
        TOPIC_TABLE_ID,
        "--record-id",
        topic_record_id,
        "--json",
        json.dumps(patch, ensure_ascii=False),
    ]
    run_lark_json(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate article material package from today's top recommended topic.")
    parser.add_argument("--write", action="store_true", help="write package into article production Base")
    args = parser.parse_args()

    topic = get_top_topic()
    record = build_article_record(topic)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "topic": topic.get("选题标题"), "record": record}, ensure_ascii=False, indent=2))
        return 0

    article_record_id = create_article_record(record)
    time.sleep(0.8)
    update_topic_status(topic["record_id"])
    print(json.dumps({"ok": True, "article_record_id": article_record_id, "topic": topic.get("选题标题"), "article_theme": record["文章主题"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
