#!/usr/bin/env python3
"""Publish a selected agent skill into a Feishu/Lark Wiki skill library."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SkillMetadata:
    path: Path
    name: str
    description: str
    body: str
    frontmatter: dict[str, Any]
    resource_files: list[str]
    has_openai_metadata: bool
    digest: str


def parse_skill(skill_dir: Path | str) -> SkillMetadata:
    path = Path(skill_dir).expanduser().resolve()
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"Missing SKILL.md in {path}")

    raw = skill_md.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(raw)
    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()
    if not name:
        raise ValueError(f"Missing required frontmatter field 'name' in {skill_md}")
    if not description:
        raise ValueError(f"Missing required frontmatter field 'description' in {skill_md}")

    resource_files = _list_resource_files(path)
    digest = _hash_skill(path)
    return SkillMetadata(
        path=path,
        name=name,
        description=description,
        body=body.strip(),
        frontmatter=frontmatter,
        resource_files=resource_files,
        has_openai_metadata=(path / "agents" / "openai.yaml").exists(),
        digest=digest,
    )


def _parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = raw.find("\n---", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed with ---")
    frontmatter_text = raw[4:end]
    body = raw[end + 4 :]
    parsed = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(parsed, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML mapping")
    return parsed, body


def _list_resource_files(path: Path) -> list[str]:
    files: list[str] = []
    for dirname in ("agents", "references", "scripts", "assets"):
        root = path / dirname
        if not root.exists():
            continue
        for file in sorted(p for p in root.rglob("*") if p.is_file()):
            if "__pycache__" in file.parts:
                continue
            files.append(file.relative_to(path).as_posix())
    return files


def _hash_skill(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        if "__pycache__" in file.parts:
            continue
        if ".pytest_cache" in file.parts:
            continue
        rel = file.relative_to(path).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def derive_short_title(description: str, max_len: int = 80) -> str:
    first = re.split(r"(?<=[.!?。！？])\s+", description.strip(), maxsplit=1)[0]
    first = first.rstrip(".。!！?？").strip()
    if len(first) <= max_len:
        return first
    return first[: max_len - 1].rstrip() + "..."


def build_plain_language_summary(name: str, description: str) -> str:
    summaries = {
        "sc": "这是技能上架工具：把本地技能打包，发布到飞书 AI 技能库，生成说明页、附件和总索引，并检查页面和附件能不能用。",
        "xx": "这是把研究资料变成知识库的工作流：围绕一个主题找资料、筛来源、提炼方法和清单，再整理成中文学习内容发布到飞书。",
        "zsk": "这是诸葛资本知识库的导航规则：告诉 Agent 该先读哪些页面、资料放到哪里、研究报告和会议纪要该按什么结构写。",
    }
    return summaries.get(name, f"这个技能的用途是：{description}")


def build_skill_page_xml(metadata: SkillMetadata, attachment_name: str) -> str:
    short_title = derive_short_title(metadata.description)
    plain_summary = build_plain_language_summary(metadata.name, metadata.description)
    resource_rows = "\n".join(
        f"<tr><td>{_x(path)}</td><td>{_resource_guidance(path)}</td></tr>" for path in metadata.resource_files
    )
    if not resource_rows:
        resource_rows = "<tr><td>无</td><td>该技能没有附加资源，读取本页即可。</td></tr>"

    frontmatter_yaml = yaml.safe_dump(metadata.frontmatter, allow_unicode=True, sort_keys=False).strip()
    body_excerpt = metadata.body[:2500]
    if len(metadata.body) > 2500:
        body_excerpt += "\n\n[Truncated in Feishu runtime page. Download attachment for full SKILL.md.]"

    return f"""<title>{_x(metadata.name)} - {_x(short_title)}</title>

<callout emoji="✅" background-color="light-green" border-color="green">
  <p>Agent 默认先读取本页即可使用该技能；只有需要本地安装、脚本、assets 或完整 references 时才下载附件包。</p>
</callout>

<h1>Identity And Trigger</h1>
<table>
  <thead><tr><th background-color="light-gray">字段</th><th background-color="light-gray">内容</th></tr></thead>
  <tbody>
    <tr><td>技能名</td><td>{_x(metadata.name)}</td></tr>
    <tr><td>唯一 ID</td><td>{_x(metadata.name)}</td></tr>
    <tr><td>用途</td><td>{_x(metadata.description)}</td></tr>
    <tr><td>OpenAI metadata</td><td>{"yes" if metadata.has_openai_metadata else "no"}</td></tr>
    <tr><td>Content hash</td><td>{metadata.digest}</td></tr>
  </tbody>
</table>

<h1>大白话说明</h1>
<callout emoji="💬" background-color="light-yellow" border-color="yellow">
  <p>这个技能帮 Agent 做什么：{_x(plain_summary)}</p>
  <p>大多数情况下，Agent 读完这个页面就能按流程做事；只有要本地安装、运行脚本、查看完整 references 或迁移给其他 Agent 时，才需要下载附件包。</p>
</callout>

<h1>Agent Runtime Guide</h1>
<ol>
  <li seq="auto">先判断用户请求是否匹配上方用途和触发场景。</li>
  <li seq="auto">读取本页的最小流程和资源清单，优先只加载任务需要的部分。</li>
  <li seq="auto">如果 references、scripts 或 assets 对当前任务必要，再下载附件包。</li>
  <li seq="auto">涉及飞书写入、发布、外部系统变更时，遵守调用 Agent 的外部动作边界。</li>
</ol>

<h1>Quick Decision</h1>
<table>
  <thead><tr><th background-color="light-gray">目标</th><th background-color="light-gray">推荐路径</th></tr></thead>
  <tbody>
    <tr><td>只需要理解这个技能怎么工作</td><td>读取本页即可，不下载附件。</td></tr>
    <tr><td>需要达到本地安装效果</td><td>使用 Self-Install From Feishu 下载附件并安装。</td></tr>
    <tr><td>需要执行脚本、读取完整 references 或迁移到其他 Agent</td><td>必须下载附件。</td></tr>
  </tbody>
</table>

<h1>Platform Adapters</h1>
<table>
  <thead><tr><th background-color="light-gray">平台</th><th background-color="light-gray">调用方式</th></tr></thead>
  <tbody>
    <tr><td>Codex</td><td>在任务匹配时使用本页作为运行指南；如需安装，把附件解压到 CODEX_HOME/skills 或 ~/.codex/skills。</td></tr>
    <tr><td>Claude Code</td><td>读取本页确认触发条件；如需本地 Skill，把附件解压到 Claude 可发现的 skills 目录。</td></tr>
    <tr><td>OpenClaw</td><td>将本页作为 agent-readable protocol；需要完整文件时下载附件并按 OpenClaw skill 目录约定安装。</td></tr>
    <tr><td>Hemes</td><td>优先读取 Runtime Guide；如果 Hemes 需要本地技能文件，再下载附件迁移。</td></tr>
  </tbody>
</table>

<h1>On-Demand Resource Map</h1>
<table>
  <thead><tr><th background-color="light-gray">资源</th><th background-color="light-gray">何时读取或下载</th></tr></thead>
  <tbody>
    {resource_rows}
  </tbody>
</table>

<h1>Original Metadata</h1>
<pre lang="yaml" caption="SKILL.md frontmatter"><code>{_x(frontmatter_yaml)}</code></pre>

<h1>SKILL.md Runtime Excerpt</h1>
<pre lang="markdown" caption="SKILL.md body excerpt"><code>{_x(body_excerpt)}</code></pre>

<h1>Download And Installation</h1>
<callout emoji="ℹ️" background-color="light-blue" border-color="blue">
  <p>附件包 { _x(attachment_name) } 包含完整技能目录。只在需要安装、迁移或读取完整资源时下载。</p>
</callout>

<h1>Self-Install From Feishu</h1>
<p>当前附件 token：<code>__SC_ATTACHMENT_TOKEN__</code></p>
<pre lang="bash" caption="下载附件"><code>lark-cli docs +media-download --as user --token __SC_ATTACHMENT_TOKEN__ --output {_x(metadata.name)}-skill --overwrite</code></pre>
<pre lang="bash" caption="解压附件"><code>tar -xzf {_x(metadata.name)}-skill.gz</code></pre>
<pre lang="bash" caption="安装到 Codex"><code>mkdir -p ~/.codex/skills
cp -a {_x(metadata.name)} ~/.codex/skills/{_x(metadata.name)}</code></pre>
<pre lang="bash" caption="安装后发布技能"><code>PYTHONPATH=~/.codex/skills python3 ~/.codex/skills/{_x(metadata.name)}/scripts/publish_skill_to_lark.py /path/to/skill --space-name AI技能库</code></pre>

<h1>Page-Only Fallback</h1>
<ol>
  <li seq="auto">如果当前 Agent 不能下载附件，先按本页 Runtime Guide 执行。</li>
  <li seq="auto">如果任务需要本地脚本，告诉用户必须启用附件下载或把附件安装到 Agent 可访问目录。</li>
  <li seq="auto">不要凭空重写脚本；以附件中的脚本作为确定性实现来源。</li>
</ol>

<h1>Current Attachment Manifest</h1>
<ul>
  <li>SKILL.md</li>
  <li>agents/openai.yaml（如果存在）</li>
  <li>scripts/（如果存在）</li>
  <li>references/（如果存在）</li>
  <li>assets/（如果存在）</li>
</ul>

<h1>Version Record</h1>
<table>
  <thead><tr><th background-color="light-gray">时间</th><th background-color="light-gray">来源路径</th><th background-color="light-gray">hash</th></tr></thead>
  <tbody><tr><td>{datetime.now(timezone.utc).isoformat()}</td><td>{_x(str(metadata.path))}</td><td>{metadata.digest}</td></tr></tbody>
</table>

<h1>Verification</h1>
<checkbox done="false">页面已发布并可 fetch。</checkbox>
<checkbox done="false">附件已上传并可下载。</checkbox>
"""


def _resource_guidance(path: str) -> str:
    if path.startswith("references/"):
        return "仅当该主题细节对当前任务必要时读取。"
    if path.startswith("scripts/"):
        return "需要确定性执行或本地安装时下载附件后运行。"
    if path.startswith("assets/"):
        return "生成输出依赖素材时下载附件。"
    if path == "agents/openai.yaml":
        return "需要 OpenAI/Codex UI 元数据时读取。"
    return "按需读取。"


def create_archive(skill_dir: Path | str, output_path: Path | str) -> Path:
    source = Path(skill_dir).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as tar:
        tar.add(source, arcname=source.name, filter=_tar_filter)
    return output


def _tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(info.name).parts
    ignored = {"__pycache__", ".pytest_cache"}
    if any(part in ignored for part in parts):
        return None
    return info


def _x(value: str) -> str:
    return escape(value, quote=True)


def run_lark(args: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        ["lark-cli", *args],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"lark-cli {' '.join(args)} failed with exit {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed.stdout


def extract_json(stdout: str) -> dict[str, Any]:
    start = stdout.find("{")
    end = stdout.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON object found in output: {stdout}")
    return json.loads(stdout[start : end + 1])


def find_or_create_space(space_name: str) -> str:
    stdout = run_lark(["wiki", "+space-list", "--as", "user"])
    data = extract_json(stdout).get("data", {})
    for item in data.get("spaces", []) or data.get("items", []):
        if item.get("name") == space_name:
            return str(item.get("space_id"))
    created = extract_json(
        run_lark(
            [
                "wiki",
                "+space-create",
                "--as",
                "user",
                "--name",
                space_name,
                "--description",
                "Agent-readable skill library.",
            ]
        )
    )
    return str(created["data"]["space_id"])


def list_nodes(space_id: str) -> list[dict[str, Any]]:
    stdout = run_lark(["wiki", "+node-list", "--as", "user", "--space-id", space_id, "--page-all"])
    return list(extract_json(stdout).get("data", {}).get("nodes", []))


def find_node(nodes: list[dict[str, Any]], title: str) -> dict[str, Any] | None:
    for node in nodes:
        if node.get("title") == title:
            return node
    return None


def find_skill_node(nodes: list[dict[str, Any]], skill_name: str, preferred_title: str) -> dict[str, Any] | None:
    prefix = f"{skill_name} - "
    matches = [node for node in nodes if str(node.get("title", "")).startswith(prefix)]
    if not matches:
        return find_node(nodes, preferred_title)
    versioned = [node for node in matches if re.search(r"v\d+(?:\.\d+)?", str(node.get("title", "")), flags=re.IGNORECASE)]
    if versioned:
        return sorted(versioned, key=lambda node: len(str(node.get("title", ""))), reverse=True)[0]
    exact = find_node(nodes, preferred_title)
    if exact:
        return exact
    # If a description change alters the title, keep updating an existing page
    # instead of creating a duplicate. Longer titles usually preserve the newest
    # richer description when historical versions exist.
    return sorted(matches, key=lambda node: len(str(node.get("title", ""))), reverse=True)[0]


def find_index_node(nodes: list[dict[str, Any]]) -> dict[str, Any] | None:
    for title in ("00_技能库总索引", "AI技能库总索引"):
        node = find_node(nodes, title)
        if node:
            return node
    return None


def create_node(space_id: str, title: str) -> dict[str, Any]:
    return extract_json(
        run_lark(["wiki", "+node-create", "--as", "user", "--space-id", space_id, "--title", title])
    )["data"]


def build_index_xml(entries: list[dict[str, str]]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{_x(entry['name'])}</td>"
        f"<td>{_x(entry.get('plain_summary') or build_plain_language_summary(entry['name'], entry['description']))}</td>"
        f"<td>{_x(entry.get('platforms', 'Codex, Claude Code, OpenClaw, Hemes'))}</td>"
        f"<td><a href=\"{_x(entry['url'])}\">{_x(entry['name'])}</a></td>"
        f"<td>{_x(entry['updated_at'])}</td>"
        "</tr>"
        for entry in sorted(entries, key=lambda item: item["name"])
    )
    return f"""<title>00_技能库总索引</title>
<callout emoji="✅" background-color="light-green" border-color="green">
  <p>这个知识库收录用户主动登记的高价值 Agent 技能。Agent 先读索引定位技能，再读技能页运行指南。</p>
</callout>
<h1>大白话说明</h1>
<callout emoji="💬" background-color="light-yellow" border-color="yellow">
  <p>这个知识库不是普通资料库，而是给 AI Agent 用的“技能说明书目录”。每一行是一项技能：点进去可以看到它适合什么时候用、具体怎么用、要不要下载完整技能包。</p>
  <p>主索引只保留 00_技能库总索引；旧名 AI技能库总索引 只作为历史兼容名，不应再新建第二份索引。</p>
</callout>
<h1>Skill Index</h1>
<table>
  <thead><tr><th background-color="light-gray">技能名</th><th background-color="light-gray">大白话用途</th><th background-color="light-gray">平台</th><th background-color="light-gray">链接</th><th background-color="light-gray">更新时间</th></tr></thead>
  <tbody>
    {rows}
  </tbody>
</table>
"""


def build_index_entries(nodes: list[dict[str, Any]], current: SkillMetadata, current_url: str) -> list[dict[str, str]]:
    now = datetime.now(timezone.utc).isoformat()
    entries: dict[str, dict[str, str]] = {}
    for node in nodes:
        title = str(node.get("title", ""))
        if not title or title == "00_技能库总索引":
            continue
        name = title.split(" - ", 1)[0].strip()
        if not name:
            continue
        entries[name] = {
            "name": name,
            "description": title.split(" - ", 1)[1] if " - " in title else "",
            "platforms": "Codex, Claude Code, OpenClaw, Hemes",
            "url": str(node.get("url") or f"https://my.feishu.cn/wiki/{node.get('node_token', '')}"),
            "updated_at": "",
        }
    entries[current.name] = {
        "name": current.name,
        "description": current.description,
        "plain_summary": build_plain_language_summary(current.name, current.description),
        "platforms": "Codex, Claude Code, OpenClaw, Hemes",
        "url": current_url,
        "updated_at": now,
    }
    return list(entries.values())


def publish(skill_dir: Path, space_name: str) -> dict[str, Any]:
    metadata = parse_skill(skill_dir)
    workdir = Path(tempfile.mkdtemp(prefix="sc-publish-"))
    try:
        archive = create_archive(metadata.path, workdir / f"{metadata.name}-skill.tar.gz")
        xml_path = workdir / f"{metadata.name}.xml"
        xml_path.write_text(build_skill_page_xml(metadata, archive.name), encoding="utf-8")

        space_id = find_or_create_space(space_name)
        nodes = list_nodes(space_id)
        index_node = find_index_node(nodes) or create_node(space_id, "00_技能库总索引")
        skill_title = f"{metadata.name} - {derive_short_title(metadata.description)}"
        skill_node = find_skill_node(nodes, metadata.name, skill_title) or create_node(space_id, skill_title)

        run_lark(
            [
                "docs",
                "+update",
                "--api-version",
                "v2",
                "--as",
                "user",
                "--doc",
                str(skill_node["obj_token"]),
                "--command",
                "overwrite",
                "--content",
                f"@{xml_path.name}",
            ],
            cwd=workdir,
        )
        media = extract_json(
            run_lark(
                [
                    "docs",
                    "+media-insert",
                    "--as",
                    "user",
                    "--doc",
                    str(skill_node["obj_token"]),
                    "--type",
                    "file",
                    "--file",
                    archive.name,
                    "--file-view",
                    "card",
                ],
                cwd=workdir,
            )
        )
        file_token = media["data"]["file_token"]
        run_lark(
            [
                "docs",
                "+update",
                "--api-version",
                "v2",
                "--as",
                "user",
                "--doc",
                str(skill_node["obj_token"]),
                "--command",
                "str_replace",
                "--pattern",
                "__SC_ATTACHMENT_TOKEN__",
                "--content",
                file_token,
            ]
        )

        skill_fetch = extract_json(
            run_lark(
                [
                    "docs",
                    "+fetch",
                    "--api-version",
                    "v2",
                    "--as",
                    "user",
                    "--doc",
                    str(skill_node["obj_token"]),
                    "--scope",
                    "keyword",
                    "--keyword",
                    "Agent Runtime Guide|Platform Adapters",
                ]
            )
        )
        content = skill_fetch["data"]["document"]["content"]
        downloaded = workdir / f"downloaded-{archive.name}"
        run_lark(
            [
                "docs",
                "+media-download",
                "--as",
                "user",
                "--token",
                file_token,
                "--output",
                downloaded.name,
                "--overwrite",
            ],
            cwd=workdir,
        )
        downloaded_paths = list(workdir.glob(f"{downloaded.name}*"))
        attachment_downloaded = bool(downloaded_paths)

        skill_url = str(skill_node.get("url") or f"https://my.feishu.cn/wiki/{skill_node['node_token']}")
        index_xml = workdir / "index.xml"
        updated_nodes = list_nodes(space_id)
        index_xml.write_text(build_index_xml(build_index_entries(updated_nodes, metadata, skill_url)), encoding="utf-8")
        run_lark(
            [
                "docs",
                "+update",
                "--api-version",
                "v2",
                "--as",
                "user",
                "--doc",
                str(index_node["obj_token"]),
                "--command",
                "overwrite",
                "--content",
                f"@{index_xml.name}",
            ],
            cwd=workdir,
        )
        return {
            "space_id": space_id,
            "index_url": str(index_node.get("url") or f"https://my.feishu.cn/wiki/{index_node['node_token']}"),
            "skill_url": skill_url,
            "skill_doc": str(skill_node["obj_token"]),
            "file_token": file_token,
            "attachment_downloaded": attachment_downloaded,
            "verified": "Agent Runtime Guide" in content and "Platform Adapters" in content and attachment_downloaded,
            "hash": metadata.digest,
        }
    finally:
        if os.environ.get("SC_KEEP_WORKDIR") != "1":
            shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a skill directory to a Feishu/Lark skill library.")
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--space-name", default="AI技能库")
    args = parser.parse_args()

    result = publish(args.skill_dir, args.space_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
