import tarfile
import tempfile
import unittest
from pathlib import Path

from sc.scripts.publish_skill_to_lark import (
    build_index_xml,
    build_plain_language_summary,
    build_skill_page_xml,
    create_archive,
    derive_short_title,
    parse_skill,
)


class PublishSkillToLarkTests(unittest.TestCase):
    def test_parse_skill_reads_frontmatter_and_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo-skill"
            (skill / "references").mkdir(parents=True)
            (skill / "agents").mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Use when testing demo skills.\n---\n\n# Demo\n\nBody.",
                encoding="utf-8",
            )
            (skill / "references" / "guide.md").write_text("# Guide", encoding="utf-8")
            (skill / "agents" / "openai.yaml").write_text("interface:\n  display_name: Demo\n", encoding="utf-8")

            metadata = parse_skill(skill)

        self.assertEqual(metadata.name, "demo-skill")
        self.assertEqual(metadata.description, "Use when testing demo skills.")
        self.assertTrue(metadata.has_openai_metadata)
        self.assertIn("references/guide.md", metadata.resource_files)

    def test_derive_short_title_uses_human_phrase(self):
        self.assertEqual(
            derive_short_title("Evidence-driven research and Feishu/Lark knowledge-base publishing workflow."),
            "Evidence-driven research and Feishu/Lark knowledge-base publishing workflow",
        )

    def test_build_plain_language_summary_uses_known_skill_explanations(self):
        self.assertIn("上架工具", build_plain_language_summary("sc", "Publish skills."))
        self.assertIn("研究资料变成知识库", build_plain_language_summary("xx", "Research."))
        self.assertIn("诸葛资本知识库", build_plain_language_summary("zsk", "Route knowledge."))

    def test_build_skill_page_xml_escapes_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "escaping"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: escaping\ndescription: Use when A & B < C.\n---\n\n# Body\n",
                encoding="utf-8",
            )
            metadata = parse_skill(skill)

        xml = build_skill_page_xml(metadata, attachment_name="escaping.tar.gz")

        self.assertIn("<title>escaping - Use when A &amp; B &lt; C</title>", xml)
        self.assertIn("Agent Runtime Guide", xml)
        self.assertIn("Codex", xml)
        self.assertIn("Claude Code", xml)
        self.assertIn("OpenClaw", xml)
        self.assertIn("Hemes", xml)
        self.assertIn("Quick Decision", xml)
        self.assertIn("大白话说明", xml)
        self.assertIn("这个技能帮 Agent 做什么", xml)
        self.assertIn("Self-Install From Feishu", xml)
        self.assertIn("__SC_ATTACHMENT_TOKEN__", xml)
        self.assertIn("docs +media-download", xml)

    def test_create_archive_contains_skill_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "archive-skill"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: archive-skill\ndescription: Use when archiving.\n---\n\n# Archive",
                encoding="utf-8",
            )
            (skill / "references" / "notes.md").write_text("notes", encoding="utf-8")
            output = root / "archive-skill.tar.gz"

            create_archive(skill, output)

            with tarfile.open(output, "r:gz") as tar:
                names = tar.getnames()

        self.assertIn("archive-skill/SKILL.md", names)
        self.assertIn("archive-skill/references/notes.md", names)

    def test_build_index_xml_keeps_multiple_skill_entries(self):
        entries = [
            {
                "name": "sc",
                "description": "Publish skills.",
                "platforms": "Codex, Claude Code, OpenClaw, Hemes",
                "url": "https://example.com/sc",
                "updated_at": "2026-05-28T00:00:00+00:00",
            },
            {
                "name": "xx",
                "description": "Research into Feishu knowledge bases.",
                "platforms": "Codex",
                "url": "https://example.com/xx",
                "updated_at": "2026-05-28T00:01:00+00:00",
            },
        ]

        xml = build_index_xml(entries)

        self.assertIn("https://example.com/sc", xml)
        self.assertIn("https://example.com/xx", xml)
        self.assertIn("<td>sc</td>", xml)
        self.assertIn("<td>xx</td>", xml)
        self.assertIn("大白话用途", xml)
        self.assertIn("这是技能上架工具", xml)
        self.assertIn("这是把研究资料变成知识库的工作流", xml)
        self.assertIn("这个知识库不是普通资料库", xml)
        self.assertIn("主索引只保留 00_技能库总索引", xml)


if __name__ == "__main__":
    unittest.main()
