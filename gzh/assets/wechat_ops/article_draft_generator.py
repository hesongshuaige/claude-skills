#!/usr/bin/env python3
"""Generate a review-only WeChat article draft and link it back to Feishu Base."""

from __future__ import annotations

import argparse
import html
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
    "标题备选",
    "文章结构",
    "表达边界",
    "策略卡结论",
    "AI预审结论",
    "AI预审理由",
    "可对外表达程度",
    "内部确认清单",
    "修改建议",
    "AI预审状态",
    "初稿链接",
    "本文转化目标",
    "期望动作",
    "文章结尾承接口径",
    "发布后跟进建议",
    "承接动作",
    "分发对象",
    "来源材料链接",
    "审稿意见/复盘结论",
]


def run_lark_json(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def xml_text(value: Any) -> str:
    return html.escape(str(value or ""), quote=False).replace("\n", "<br/>")


def split_lines(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [line.strip() for line in str(value or "").splitlines() if line.strip()]


def first_title(record: dict[str, Any]) -> str:
    for line in split_lines(record.get("标题备选")):
        cleaned = line
        for prefix in ("1. ", "1、", "一、"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :]
        if cleaned:
            return cleaned
    return record.get("文章主题") or "诸葛资本公众号待审初稿"


def _parse_package(record: dict[str, Any]) -> dict[str, Any]:
    """Extract structured sections from the material package summary."""
    import re

    package = str(record.get("资料包摘要") or "")
    result: dict[str, Any] = {
        "core_points": [],
        "key_data": [],
        "framework": [],
        "keywords": [],
        "opportunity_lines": [],
        "source_ref": "",
    }

    def extract_section(marker: str) -> str:
        m = re.search(rf"【{marker}】\s*(.+?)(?=\n【|$)", package, re.DOTALL)
        return m.group(1).strip() if m else ""

    # Core points
    points_text = extract_section("政策核心要点")
    if points_text:
        result["core_points"] = [
            line.lstrip("- •").strip()
            for line in points_text.split("\n")
            if line.strip() and not line.strip().startswith("【")
        ]

    # Key data
    data_text = extract_section("关键量化指标")
    if data_text:
        result["key_data"] = [d.strip() for d in data_text.split("；") if d.strip() and len(d.strip()) > 5]

    # Framework
    fw_text = extract_section("政策框架")
    if fw_text:
        result["framework"] = [f.strip() for f in fw_text.split("→") if f.strip()]

    # Keywords
    kw_text = extract_section("产业关键词")
    if kw_text:
        result["keywords"] = [k.strip() for k in kw_text.split("、") if k.strip()]

    # Opportunity
    opp_text = extract_section("诸葛资本机会")
    if opp_text:
        result["opportunity_lines"] = [l.strip() for l in opp_text.split("\n") if l.strip()]

    # Source reference
    src_text = extract_section("原文参考")
    if src_text:
        result["source_ref"] = src_text[:800]

    return result


def make_body_paragraphs(record: dict[str, Any]) -> list[str]:
    """Generate article body paragraphs using structured material package data."""
    theme = record.get("文章主题") or "当前产业选题"
    service_line = first_select(record.get("服务主线"))
    ending = record.get("文章结尾承接口径") or ""
    core = record.get("核心观点") or "这篇文章应围绕公开政策、产业趋势和诸葛资本服务区域产业发展的实际价值展开。"
    structure_items = split_lines(record.get("文章结构"))

    # Parse the structured package summary
    parsed = _parse_package(record)
    data = parsed["key_data"]
    points = parsed["core_points"]
    framework = parsed["framework"]
    keywords = parsed["keywords"]
    opp_lines = parsed["opportunity_lines"]
    kw_text = "、".join(keywords[:3]) if keywords else "产业"

    paragraphs: list[str] = []

    # ── Opening: use real data if available ──
    if data:
        # Quote the most impressive data point
        best_data = data[0][:80] if data else ""
        paragraphs.append(
            f"一份刚落地的产业政策明确了量化目标——{best_data}。数字背后是{kw_text}领域正在加速的产业升级信号。对{kw_text}企业来说，真正的机会不在于政策文件本身，而在于能不能找到把技术、场景、资本和产业资源连接起来的平台。"
        )
    else:
        paragraphs.append(
            f"一项产业政策真正产生价值，不在于文件停留在纸面，而在于能不能变成企业看得见、用得上的场景、资源和协同。{kw_text}领域正在进入政策驱动的产业加速期，关键在于谁能把政策红利转化为具体的企业服务能力。"
        )

    # ── Core viewpoint ──
    paragraphs.append(core)

    # ── Role paragraph: based on service line ──
    if service_line == "领导认可型":
        paragraphs.append(
            "对区域国资基金平台而言，公众号文章不能只停留在政策转述，而要说明公司如何围绕区域发展要求，把国资功能、基金工具和产业培育结合起来。"
        )
    elif service_line == "投资机构合作型":
        paragraphs.append(
            "对投资机构和专业服务机构而言，真正有价值的合作基础，不只是资金规模，而是区域项目触达、产业场景、政策理解和长期协同能力。"
        )
    else:
        paragraphs.append(
            f"对{kw_text}项目方而言，真正难的往往不是看见政策，而是把技术、产品、场景、资金、空间和合作伙伴有效连接起来。"
        )

    # ── Policy substance: use extracted core points ──
    if points:
        # Present 2-3 key policy points as substance
        substance_points = points[:3]
        substance_text = "；".join(substance_points)
        paragraphs.append(
            f"从政策内容看，有几个方向值得{kw_text}企业重点关注：{substance_text}。这些方向背后，是{kw_text}从技术突破走向产业化落地的系统需求。"
        )
    elif structure_items:
        # Fallback to structure items
        for item in structure_items[:2]:
            cleaned = item
            for prefix in ("第一部分：", "第二部分：", "第三部分：", "第四部分：", "第五部分："):
                cleaned = cleaned.replace(prefix, "")
            if cleaned:
                paragraphs.append(cleaned)

    # ── Key data highlight ──
    if data and len(data) >= 2:
        data_summary = "；".join(d[:50] for d in data[:4])
        paragraphs.append(
            f"政策设定的量化目标值得关注：{data_summary}。这些指标意味着{kw_text}领域在未来几年将出现大量的企业成长和产业整合机会。"
        )

    # ── Zhuge Capital opportunity: use extracted mapping ──
    if opp_lines:
        # Find the most relevant opportunity line
        for line in opp_lines:
            if "💡" in line or "对项目方" in line or "领导关注" in line or "机构合作" in line:
                clean_line = line.lstrip("💡⏰📊📌").strip()
                if clean_line:
                    paragraphs.append(clean_line)
                    break

    # ── Local policy connection ──
    package = str(record.get("资料包摘要") or "")
    if "【本地政策/区域连接】" in package:
        paragraphs.append(
            "结合公开政策和本地产业资源，文章可以进一步说明区域政策、产业载体、场景资源和资本工具之间的关系，但所有具体政策名称、数据和条款都必须在发布前重新核验。"
        )

    # ── Compliance guard ──
    paragraphs.extend(
        [
            "对外表达必须保持克制：可以讲政策背景、产业趋势、区域资源和服务能力，不能写成基金产品推介、投资邀约、收益承诺或对具体项目的未授权披露。",
            ending or "欢迎相关项目方和合作机构在合规边界内开展产业交流，共同推动更多优质项目对接真实场景、区域资源和长期资本。",
        ]
    )
    return paragraphs


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
        cmd.extend(["--view-id", PENDING_DRAFT_VIEW_ID, "--limit", "1"])
    cmd.extend(["--format", "json"])
    for field in READ_FIELDS:
        cmd.extend(["--field-id", field])
    data = run_lark_json(cmd)["data"]
    if not data.get("record_id_list") or data.get("record_not_found"):
        raise RuntimeError("没有待生成初稿的文章生产记录")
    row = dict(zip(data["fields"], data["data"][0]))
    row["record_id"] = data["record_id_list"][0]
    return row


def quality_guard(record: dict[str, Any]) -> tuple[str, str]:
    precheck = first_select(record.get("AI预审结论"))
    investment_confirm = first_select(record.get("投资部确认"))
    fact_status = first_select(record.get("事实核验状态"))
    if precheck == "不建议写":
        return "暂缓", "AI（人工智能）预审为不建议写，不生成初稿。"
    if precheck == "必须人工确认" or investment_confirm == "待确认":
        return "已生成待确认", "这是内部讨论版初稿，不可直接发布；投资部确认前，不进入部长审。"
    if fact_status in {"未核验", "有疑点"}:
        return "已生成待确认", "事实尚未充分核验，只能作为内部讨论版。"
    return "已生成可送审", "已生成可送审初稿，但仍必须走合规审查和人工终审。"


def build_body(record: dict[str, Any]) -> str:
    title = first_title(record)
    service_line = first_select(record.get("服务主线"))
    readers = "、".join(record.get("目标读者") or [])
    precheck = first_select(record.get("AI预审结论"))
    public_level = first_select(record.get("可对外表达程度"))
    draft_status, draft_note = quality_guard(record)
    column = first_select(record.get("内容栏目"))
    confirm_items = split_lines(record.get("内部确认清单"))
    modify_items = split_lines(record.get("修改建议"))
    boundary_items = split_lines(record.get("表达边界"))
    source_link = record.get("来源材料链接") or ""

    paragraphs = make_body_paragraphs(record)

    confirm_rows = "".join(
        f"<tr><td>{xml_text(item)}</td><td>待确认</td></tr>" for item in confirm_items[:8]
    )
    modify_rows = "".join(
        f"<tr><td>{xml_text(item)}</td><td>初稿修改时执行</td></tr>" for item in modify_items[:6]
    )
    boundary_rows = "".join(
        f"<tr><td>{xml_text(item)}</td></tr>" for item in boundary_items[:8]
    )
    title_options = "".join(f"<li>{xml_text(line)}</li>" for line in split_lines(record.get("标题备选"))[:6])
    body_paragraphs = "\n".join(f"<p>{xml_text(p)}</p>" for p in paragraphs)
    source_block = f'<p><a type="url-preview" href="{html.escape(source_link, quote=True)}">来源材料链接</a></p>' if source_link else ""

    return f"""<title>{xml_text(title)}（待审初稿）</title>
<callout emoji="⚠️" background-color="light-yellow" border-color="yellow">
  <p><b>内部待审稿，不可直接发布。</b>{xml_text(draft_note)}</p>
  <p>AI（人工智能）预审结论：{xml_text(precheck)}；可对外表达程度：{xml_text(public_level)}。</p>
</callout>
<h1>一、稿件定位</h1>
<table>
  <thead><tr><th background-color="light-gray">项目</th><th background-color="light-gray">内容</th></tr></thead>
  <tbody>
    <tr><td>服务主线</td><td>{xml_text(service_line)}</td></tr>
    <tr><td>内容栏目</td><td>{xml_text(column)}</td></tr>
    <tr><td>目标读者</td><td>{xml_text(readers)}</td></tr>
    <tr><td>当前状态</td><td>{xml_text(draft_status)}</td></tr>
    <tr><td>本文转化目标</td><td>{xml_text(record.get("本文转化目标"))}</td></tr>
    <tr><td>期望动作</td><td>{xml_text(record.get("期望动作"))}</td></tr>
    <tr><td>核心观点</td><td>{xml_text(record.get("核心观点"))}</td></tr>
  </tbody>
</table>
<h1>二、标题备选</h1>
<ul>{title_options}</ul>
<hr/>
<h1>三、公众号正文待审稿</h1>
<h2>{xml_text(title)}</h2>
{body_paragraphs}
<hr/>
<h1>四、发布前确认清单</h1>
<table>
  <thead><tr><th background-color="light-gray">必须确认的问题</th><th background-color="light-gray">状态</th></tr></thead>
  <tbody>{confirm_rows}</tbody>
</table>
<h1>五、修改建议和表达边界</h1>
<grid>
  <column width-ratio="0.5">
    <h2>修改建议</h2>
    <table><tbody>{modify_rows}</tbody></table>
  </column>
  <column width-ratio="0.5">
    <h2>表达边界</h2>
    <table><tbody>{boundary_rows}</tbody></table>
  </column>
</grid>
<h1>六、来源材料</h1>
{source_block}
<h1>七、发布后跟进建议</h1>
<p>{xml_text(record.get("发布后跟进建议"))}</p>
<p>正式发布前，必须重新核验政策原文、发文字号、发布日期和发布机关；涉及中央、省、市、区政策和领导表述，必须按权威原文表达。</p>
"""


def create_doc(content: str) -> str:
    result = subprocess.run(
        [
            "lark-cli",
            "docs",
            "+create",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--parent-position",
            "my_library",
            "--content",
            "-",
        ],
        input=content,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    data = json.loads(result.stdout)
    return data["data"]["document"]["url"]


def write_back(record: dict[str, Any], doc_url: str, draft_status: str, draft_note: str) -> None:
    review_note = (record.get("审稿意见/复盘结论") or "").rstrip()
    if review_note:
        review_note += "\n"
    review_note += f"已生成公众号待审初稿：{draft_status}。"
    patch: dict[str, Any] = {
        "初稿链接": doc_url,
        "初稿生成状态": draft_status,
        "初稿生成说明": draft_note,
        "审稿意见/复盘结论": review_note,
    }
    if draft_status == "已生成可送审":
        patch["审稿状态"] = "部长审"
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
        record["record_id"],
        "--json",
        json.dumps(patch, ensure_ascii=False),
    ]
    run_lark_json(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Zhuge Capital WeChat draft document.")
    parser.add_argument("--write", action="store_true", help="create Feishu doc and write link back to Base")
    parser.add_argument("--force", action="store_true", help="create another draft even if draft link exists")
    parser.add_argument("--record-id", default="", help="process a specific article production record")
    args = parser.parse_args()

    record = get_candidate(args.record_id)
    if first_select(record.get("AI预审状态")) != "已预审":
        raise RuntimeError("当前记录还没有完成 AI（人工智能）预审，先运行 strategy_precheck.py")
    existing_link = record.get("初稿链接") or ""
    if existing_link and not args.force:
        print(json.dumps({"ok": True, "skipped": True, "reason": "初稿链接已存在", "url": existing_link}, ensure_ascii=False, indent=2))
        return 0
    draft_status, draft_note = quality_guard(record)
    if draft_status == "暂缓":
        raise RuntimeError(draft_note)
    content = build_body(record)
    if not args.write:
        print(json.dumps({"ok": True, "dry_run": True, "article": record.get("文章主题"), "初稿生成状态": draft_status, "preview_chars": len(content)}, ensure_ascii=False, indent=2))
        return 0
    doc_url = create_doc(content)
    write_back(record, doc_url, draft_status, draft_note)
    time.sleep(0.5)
    print(json.dumps({"ok": True, "record_id": record["record_id"], "article": record.get("文章主题"), "初稿生成状态": draft_status, "url": doc_url}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
