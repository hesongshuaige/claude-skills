import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_REFERENCES = {
    "hermes-profile-and-model.md",
    "feishu-bot-and-permissions.md",
    "lark-user-authorization.md",
    "context-files-and-prompts.md",
    "troubleshooting.md",
    "security-and-handoff.md",
    "pressure-scenarios.md",
}
REQUIRED_TEMPLATES = {
    "SOUL.md.template",
    "AGENTS.md.template",
    "README.md.template",
    "PROJECT.md.template",
}


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
    if not match:
        return {}

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


class SkillPackageTests(unittest.TestCase):
    def test_all_required_references_exist(self) -> None:
        reference_dir = PACKAGE_ROOT / "references"
        present = {path.name for path in reference_dir.glob("*.md")}

        self.assertEqual(set(), REQUIRED_REFERENCES - present)

    def test_all_required_templates_exist(self) -> None:
        template_dir = PACKAGE_ROOT / "assets" / "templates"
        present = {path.name for path in template_dir.glob("*.template")}

        self.assertEqual(set(), REQUIRED_TEMPLATES - present)

    def test_skill_frontmatter_has_only_name_and_description(self) -> None:
        frontmatter = read_frontmatter(PACKAGE_ROOT / "SKILL.md")

        self.assertEqual({"name", "description"}, set(frontmatter))

    def test_skill_description_starts_with_use_when(self) -> None:
        frontmatter = read_frontmatter(PACKAGE_ROOT / "SKILL.md")

        self.assertIsInstance(frontmatter.get("description"), str)
        self.assertTrue(frontmatter["description"].startswith("Use when"))

    def test_openai_metadata_names_explicit_invocation(self) -> None:
        metadata = (PACKAGE_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("$agentgo", metadata)

    def test_package_contains_no_todo_markers(self) -> None:
        marker = "TO" + "DO"
        offenders = []
        for path in self._package_text_files():
            if marker in path.read_text(encoding="utf-8"):
                offenders.append(path.relative_to(PACKAGE_ROOT).as_posix())

        self.assertEqual([], offenders)

    def test_package_contains_no_likely_real_secrets(self) -> None:
        sensitive_suffix = "(?:APP_" + "SECRET|API[_-]?KEY|PASSWORD)"
        assignment_names = rf"[A-Z][A-Z0-9_]*{sensitive_suffix}"
        assignment = re.compile(
            rf"(?im)^\s*{assignment_names}\s*=\s*(?!<|\{{\{{|\$|test-|example|placeholder)([^\s#]+)"
        )
        feishu_identifier = re.compile(
            r"(?<![A-Za-z0-9])(?:cli|ou)_[A-Za-z0-9]{16,}(?![A-Za-z0-9])"
        )
        offenders = []
        for path in self._package_text_files():
            text = path.read_text(encoding="utf-8")
            if assignment.search(text) or feishu_identifier.search(text):
                offenders.append(path.relative_to(PACKAGE_ROOT).as_posix())

        self.assertEqual([], offenders)

    @staticmethod
    def _package_text_files() -> list[Path]:
        return sorted(
            path
            for path in PACKAGE_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".template"}
        )


if __name__ == "__main__":
    unittest.main()
