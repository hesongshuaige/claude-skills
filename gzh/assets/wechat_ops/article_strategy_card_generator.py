#!/usr/bin/env python3
"""Generate a strategy card for a Zhuge Capital WeChat article package."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any

from topic_collector import first_select


ARTICLE_BASE_TOKEN = "DMESblAlEaST94s5lBOcaoBEnyg"
ARTICLE_TABLE_ID = "tblpqQMN74IPkGOO"
PENDING_DRAFT_VIEW_ID = "vew2dpAC7B"

READ_FIELDS = [
    "文章主题",
    "内容栏目",
    "服务主线",
    "目标读者",
    "核心观点",
    "资料包摘要",
    "事实核验状态",
    "投资部确认",
    "合规结论",
    "审稿状态",
    "本文转化目标",
    "期望动作",
    "文章结尾承接口径",
    "发布后跟进建议",
    "承接动作",
    "分发对象",
]


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def get_pending_article(record_id: str = "") -> dict[str, Any]:
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
        cmd.extend(["--view-id", PENDING_DRAFT_VIEW_ID, "--limit", "1"])
    cmd.extend(["--format", "json"])
    for field in READ_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list") or data.get("record_not_found"):
        raise RuntimeError("没有待生成策略卡的文章生产记录")
    row = dict(zip(data["fields"], data["data"][0]))
    row["record_id"] = data["record_id_list"][0]
    return row


def _parse_package_fields(record: dict[str, Any]) -> dict[str, Any]:
    """Parse structured fields from the material package summary."""
    package = str(record.get("资料包摘要") or "")
    result: dict[str, Any] = {
        "core_points": [],
        "key_data": [],
        "timelines": [],
        "framework": [],
        "keywords": [],
        "opportunity": "",
        "raw_text": package,
    }

    import re

    # Extract sections between 【...】markers
    def extract_section(marker: str) -> str:
        pattern = rf"【{marker}】\s*(.+?)(?=\n【|$)"
        m = re.search(pattern, package, re.DOTALL)
        return m.group(1).strip() if m else ""

    # Parse core points (bullet list)
    points_text = extract_section("政策核心要点")
    if points_text:
        result["core_points"] = [
            line.lstrip("- •").strip()
            for line in points_text.split("\n")
            if line.strip() and not line.strip().startswith("【")
        ]

    # Parse key data (semicolon-separated)
    data_text = extract_section("关键量化指标")
    if data_text:
        result["key_data"] = [d.strip() for d in data_text.split("；") if d.strip() and len(d.strip()) > 5]

    # Parse policy framework (→ separated)
    framework_text = extract_section("政策框架")
    if framework_text:
        result["framework"] = [f.strip() for f in framework_text.split("→") if f.strip()]

    # Parse industry keywords (comma-separated)
    kw_text = extract_section("产业关键词")
    if kw_text:
        result["keywords"] = [k.strip() for k in kw_text.split("、") if k.strip()]

    # Parse opportunity section
    result["opportunity"] = extract_section("诸葛资本机会")

    # Parse timeline
    timeline_text = extract_section("时间节点")
    if timeline_text:
        result["timelines"] = [t.strip() for t in timeline_text.split("；") if t.strip()]

    return result


def title_options(record: dict[str, Any]) -> str:
    """Generate title options dynamically from structured package data."""
    parsed = _parse_package_fields(record)
    theme = record.get("文章主题") or ""
    service_line = first_select(record.get("服务主线"))
    keywords = parsed["keywords"]
    data = parsed["key_data"]
    framework = parsed["framework"]

    titles = [f"1. {theme}"]

    # Generate title based on actual data points
    if data:
        # Extract first meaningful number from data
        import re
        num_match = re.search(r"(\d+[\.\d]*)\s*(个|家|项|亿|万|条)", data[0])
        if num_match:
            num = num_match.group(0)
            kw = keywords[0] if keywords else "产业"
            titles.append(f"2. 政策定了{num}的目标，{kw}项目方接下来怎么落地")
            titles.append(f"3. 从量化指标看{kw}的产业机会与资本协同空间")

    if framework and len(framework) >= 3:
        titles.append(f"4. {keywords[0] if keywords else '产业'}政策五大方向解读：项目方最该关注什么")

    # Service-line specific title
    if service_line == "项目方引流型":
        titles.append(f"5. 不只是政策利好——{keywords[0] if keywords else '产业'}企业真正需要的是场景、资本和资源协同")
    elif service_line == "领导认可型":
        titles.append(f"5. 从政策部署到区域实践：国资基金如何服务{keywords[0] if keywords else '产业'}产业培育")
    else:
        titles.append(f"5. 政策背后的产业信号与区域合作机会")

    return "\n".join(titles[:6])


def inferred_column(service_line: str) -> str:
    if service_line == "项目方引流型":
        return "项目方指南"
    if service_line == "投资机构合作型":
        return "机构合作观察"
    if service_line == "领导认可型":
        return "区域产业生态"
    return "产业观察"


def fallback_conversion(column: str, service_line: str) -> tuple[str, str, str, str]:
    if column == "项目方指南" or service_line == "项目方引流型":
        return (
            "让项目方看到诸葛资本懂产业、懂政策、能协同区域资源，愿意发起产业交流或项目对接。",
            "项目方咨询政策、载体、场景、资本协同或提交项目交流需求。",
            "欢迎相关项目方在合规边界内围绕产业落地、政策匹配、场景对接和资本协同开展交流；本文不构成投资承诺、基金推介或收益承诺。",
            "发布后 24 小时观察项目方咨询和转发；7 天内汇总可跟进项目线索，必要时转投资部或招商对接。",
        )
    if column == "机构合作观察" or service_line == "投资机构合作型":
        return (
            "让基金、券商、律所、会计师事务所、FA、产业投资部门看到诸葛资本的区域项目触达和协同价值。",
            "合作机构提供项目线索、共研赛道、联合走访或建立常态化沟通。",
            "欢迎专业机构围绕项目线索、产业研究和区域协同开展交流；不涉及具体基金募集或收益承诺。",
            "发布后观察机构转发、私信、项目推荐和合作邀约；7 天内整理机构名单和可跟进事项。",
        )
    if column == "区域产业生态" or service_line == "领导认可型":
        return (
            "沉淀可供领导认可、对上汇报和区域品牌展示的内容资产。",
            "适合领导、国资系统和综合部转发，作为汇报材料、品牌展示和区域产业推介素材。",
            "诸葛资本将继续在合规、审慎、专业的前提下发挥国资基金平台作用，服务优质企业和产业生态建设。",
            "发布后关注领导反馈、国资系统转发和内部认可度；沉淀为汇报、招商和品牌素材。",
        )
    return (
        "提升诸葛资本在重点产业方向上的专业品牌认知。",
        "适合内部学习、朋友圈转发和后续同类选题复用。",
        "欢迎相关主体在合规边界内开展产业交流，共同关注区域产业发展和企业成长机会。",
        "发布后记录阅读、转发和外部反馈，判断是否值得扩展为系列选题。",
    )


def structure(record: dict[str, Any]) -> str:
    """Generate article structure dynamically from policy framework and key data."""
    parsed = _parse_package_fields(record)
    service_line = first_select(record.get("服务主线"))
    column = first_select(record.get("内容栏目")) or inferred_column(service_line)
    keywords = parsed["keywords"]
    data = parsed["key_data"]
    framework = parsed["framework"]
    points = parsed["core_points"]

    kw_text = "、".join(keywords[:3]) if keywords else "产业"
    header = f"栏目定位：{column}。"

    parts = [header]

    # Part 1: Opening - policy background with real data
    if data:
        parts.append(f"第一部分：用政策量化目标开场。引用关键数据（如{data[0][:40]}），用一两句话说明政策力度和产业方向，不全文搬运政策文件。")
    else:
        parts.append(f"第一部分：点明{kw_text}领域的政策背景和核心趋势，用 1-2 段讲清为什么现在值得关注。")

    # Part 2: Use actual policy framework sections
    if framework and len(framework) >= 2:
        fw_1 = framework[1] if len(framework) > 1 else framework[0]
        parts.append(f"第二部分：围绕政策核心方向「{fw_1}」，提炼与项目方和产业最相关的 2-3 个要点。{('具体包括：' + '；'.join(points[:3])) if points else '从原文中筛选与实际产业落地最相关的内容。'}")
    else:
        parts.append(f"第二部分：讲项目方真正关心的问题：{kw_text}落地需要场景、资金、政策和产业链协同，不是单点技术突破。")

    # Part 3: Regional opportunity with local policy connection
    if parsed["opportunity"]:
        opp_brief = parsed["opportunity"][:80].replace("\n", "；")
        parts.append(f"第三部分：转到区域机会。{opp_brief}...结合本地政策和产业资源说明区域承接能力。")
    else:
        parts.append(f"第三部分：转到区域机会，结合本地政策、产业载体和区域资源说明为什么区域平台能提供承接场景。")

    # Part 4: Zhuge Capital role
    if service_line == "项目方引流型":
        parts.append(f"第四部分：讲诸葛资本角色：不是承诺投资，而是用国资基金工具连接{kw_text}项目、政策、产业资源和合作机构。用具体的服务能力说明而不是空话。")
    elif service_line == "领导认可型":
        parts.append(f"第四部分：以稳妥表述收束，体现服务大局和专业能力，说明诸葛资本如何把政策要求转化为服务区域产业的具体动作。")
    else:
        parts.append(f"第四部分：释放专业合作信号，同时守住私募基金公开表达边界，设置克制的合作入口。")

    # Part 5: Call to action
    parts.append(f"第五部分：结尾设置温和合作入口，表达欢迎{kw_text}相关交流，不出现募资或收益表述。")

    return "\n".join(parts)


def expression_boundary(record: dict[str, Any]) -> str:
    investment_confirm = first_select(record.get("投资部确认"))
    fact_status = first_select(record.get("事实核验状态"))
    return (
        "可以写：政策背景、产业趋势、区域资源、国资基金服务产业的功能、诸葛资本愿意与项目方和机构交流合作。\n"
        "谨慎写：诸葛资本具体投资偏好、具体项目判断、已投项目案例、与合作方的具体关系，必须先确认口径。\n"
        "不能写：公开募集基金、承诺投资、承诺收益、保本兜底、夸大投资能力、披露未公开项目和交易信息。\n"
        f"当前前置状态：事实核验为「{fact_status}」，投资部确认为「{investment_confirm}」。在投资部未确认前，只能进入策略卡和资料包阶段，不建议直接生成发布稿。"
    )


def strategy_conclusion(record: dict[str, Any]) -> tuple[str, str]:
    service_line = first_select(record.get("服务主线"))
    column = first_select(record.get("内容栏目")) or inferred_column(service_line)
    readers = "、".join(record.get("目标读者") or [])
    investment_confirm = first_select(record.get("投资部确认"))
    fact_status = first_select(record.get("事实核验状态"))
    if investment_confirm == "待确认" or fact_status in {"未核验", "有疑点"}:
        status = "待确认"
        next_step = "建议先把策略卡发给投资部，只确认三件事：这个方向公司能不能表达、是否符合真实产业关注边界、有没有不能公开的敏感点。确认后再进初稿。"
    else:
        status = "可进初稿"
        next_step = "可以进入初稿生成，但初稿仍需合规审查和人工终审。"
    conclusion = (
        f"本文建议栏目：{column}；服务主线：{service_line}；主要读者：{readers}。核心目标不是写政策新闻，而是把政策机会转成诸葛资本的产业服务能力表达。"
        f"当前策略判断：{status}。{next_step}"
    )
    return status, conclusion


def build_strategy_card(record: dict[str, Any]) -> dict[str, Any]:
    status, conclusion = strategy_conclusion(record)
    service_line = first_select(record.get("服务主线"))
    column = first_select(record.get("内容栏目")) or inferred_column(service_line)
    target, action, ending, follow_up = fallback_conversion(column, service_line)
    return {
        "内容栏目": column,
        "标题备选": title_options(record),
        "文章结构": structure(record),
        "表达边界": expression_boundary(record),
        "策略卡结论": conclusion,
        "策略卡状态": status,
        "本文转化目标": record.get("本文转化目标") or target,
        "期望动作": record.get("期望动作") or action,
        "文章结尾承接口径": record.get("文章结尾承接口径") or ending,
        "发布后跟进建议": record.get("发布后跟进建议") or follow_up,
        "审稿意见/复盘结论": (record.get("审稿意见/复盘结论") or "") + "\n已生成文章策略卡，进入策略确认阶段。",
    }


def write_strategy(record_id: str, patch: dict[str, Any]) -> None:
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
    parser = argparse.ArgumentParser(description="Generate article strategy card for a pending article package.")
    parser.add_argument("--write", action="store_true", help="write strategy card into Feishu Base")
    parser.add_argument("--record-id", default="", help="process a specific article production record")
    args = parser.parse_args()

    record = get_pending_article(args.record_id)
    patch = build_strategy_card(record)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "article": record.get("文章主题"), "strategy": patch}, ensure_ascii=False, indent=2))
        return 0
    write_strategy(record["record_id"], patch)
    time.sleep(0.5)
    print(json.dumps({"ok": True, "record_id": record["record_id"], "article": record.get("文章主题"), "策略卡状态": patch["策略卡状态"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
