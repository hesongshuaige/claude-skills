#!/usr/bin/env python3
"""Validate an AISC Markdown card.

This script intentionally uses only the Python standard library so it can run
across Codex, Claude, OpenClaw, Hermes, and similar agent environments.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "# AISC 学习卡片",
    "## 来源信息",
    "## 摘要",
    "## 关键词",
    "## 内容分类",
    "## 核心观点",
    "## 关键知识点",
    "## 金句 / 原文摘录",
    "## 可复用价值",
    "## 价值判断与入库建议",
]

SOURCE_TYPES = {
    "逐字稿",
    "录音稿",
    "网页文章",
    "社媒帖子",
    "报告资料",
    "访谈对话",
    "飞书文档",
    "本地文件",
    "其他",
}

CONTENT_CATEGORIES = {
    "教程方法论",
    "行业观察",
    "个人经验",
    "案例拆解",
    "观点输出",
    "知识科普",
    "资料整理",
    "情绪表达",
}

RECOMMENDATIONS = {"长期参考", "可二创", "仅存档", "不建议入库"}


def section(text: str, heading: str) -> str:
    pattern = rf"^{re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def numbered_count(body: str) -> int:
    return len(re.findall(r"^\s*\d+[.、]\s+", body, flags=re.MULTILINE))


def keyword_count(body: str) -> int:
    cleaned = re.sub(r"^\s*[-*]\s*", "", body.strip(), flags=re.MULTILINE)
    parts = re.split(r"[、,，;\n]+", cleaned)
    return len([part.strip() for part in parts if part.strip()])


def extract_source_value(source_body: str, label: str) -> str:
    match = re.search(rf"^- {re.escape(label)}：(.+)$", source_body, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"Missing required heading: {heading}")

    source = section(text, "## 来源信息")
    for label in [
        "标题",
        "作者 / 发布者",
        "来源 / 平台",
        "链接",
        "发布时间",
        "来源类型",
        "获取时间",
    ]:
        value = extract_source_value(source, label)
        if not value:
            errors.append(f"Missing source field: {label}")

    source_type = extract_source_value(source, "来源类型")
    if source_type and source_type not in SOURCE_TYPES:
        errors.append(f"来源类型 must choose exactly one known value, got: {source_type}")

    summary_lines = [line.strip() for line in section(text, "## 摘要").splitlines() if line.strip()]
    if len(summary_lines) != 3:
        errors.append(f"摘要 must contain exactly 3 non-empty lines, got {len(summary_lines)}")

    keywords = keyword_count(section(text, "## 关键词"))
    if not 5 <= keywords <= 8:
        errors.append(f"关键词 must contain 5-8 items, got {keywords}")

    category = section(text, "## 内容分类").strip()
    if category not in CONTENT_CATEGORIES:
        errors.append(f"内容分类 must choose exactly one known value, got: {category}")

    core_count = numbered_count(section(text, "## 核心观点"))
    if core_count > 3:
        errors.append(f"核心观点 must contain at most 3 numbered items, got {core_count}")
    if core_count == 0:
        errors.append("核心观点 must contain at least 1 numbered item")

    knowledge_count = numbered_count(section(text, "## 关键知识点"))
    if knowledge_count < 1:
        errors.append("关键知识点 must contain at least 1 numbered item")

    quote_body = section(text, "## 金句 / 原文摘录")
    if not quote_body:
        errors.append("金句 / 原文摘录 must be exact quotes or 无")

    recommendation = section(text, "## 价值判断与入库建议")
    if not any(recommendation.startswith(item) for item in RECOMMENDATIONS):
        errors.append("价值判断与入库建议 must start with one of: 长期参考 / 可二创 / 仅存档 / 不建议入库")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate-card.py path/to/card.md", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    errors = validate(path)
    if errors:
        print("AISC card validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AISC card validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
