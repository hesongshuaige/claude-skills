import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_TOPICS = {
    "hermes-profile-and-model.md": ("profile", "model", "key_env", "workspace"),
    "feishu-bot-and-permissions.md": ("websocket", "gateway", "allowlist", "App ID"),
    "lark-user-authorization.md": ("bot-only", "user-default", "device-code", "--as user"),
    "context-files-and-prompts.md": ("SOUL.md", "AGENTS.md", "20,000", "terminal.cwd"),
    "troubleshooting.md": ("401", "App ID", "PowerShell", "gateway"),
    "security-and-handoff.md": ("rotate", "600", "allowlist", "handoff"),
    "pressure-scenarios.md": ("无技能基线风险", "使用技能后的通过信号", "评分规则"),
}
TEMPLATE_PLACEHOLDERS = {
    "SOUL.md.template": {
        "{{AGENT_NAME}}",
        "{{ONE_LINE_ROLE}}",
    },
    "AGENTS.md.template": {
        "{{PERMISSION_BOUNDARIES}}",
        "{{VERIFICATION_RULES}}",
    },
    "README.md.template": {
        "{{AGENT_NAME}}",
        "{{AUTOMATIC_CAPABILITIES}}",
        "{{ON_DEMAND_CAPABILITIES}}",
        "{{NOT_ENABLED_CAPABILITIES}}",
    },
    "PROJECT.md.template": {
        "{{PRIMARY_USERS}}",
        "{{INPUT_SOURCES}}",
        "{{OUTPUT_TARGETS}}",
    },
}
ALL_PLACEHOLDERS = {
    "{{AGENT_NAME}}",
    "{{ONE_LINE_ROLE}}",
    "{{PRIMARY_USERS}}",
    "{{INPUT_SOURCES}}",
    "{{OUTPUT_TARGETS}}",
    "{{AUTOMATIC_CAPABILITIES}}",
    "{{ON_DEMAND_CAPABILITIES}}",
    "{{NOT_ENABLED_CAPABILITIES}}",
    "{{PERMISSION_BOUNDARIES}}",
    "{{VERIFICATION_RULES}}",
}
SECRET_NAME = (
    r"(?:[A-Z][A-Z0-9_]*_)?"
    r"(?:API_KEY|ACCESS_TOKEN|REFRESH_TOKEN|CLIENT_SECRET|APP_SECRET|"
    r"PRIVATE_KEY|PASSWORD|TOKEN|SECRET)"
)
SECRET_ASSIGNMENT = re.compile(
    rf"(?im)^\s*(?:export\s+)?(?P<name>{SECRET_NAME})\s*(?:=|:)\s*(?P<value>[^#\r\n]+?)\s*$"
)
BEARER_TOKEN = re.compile(
    r"(?i)\bbearer[ \t]+(?P<value>[A-Za-z0-9._~+/=-]{12,})"
)
PRIVATE_KEY_PEM = re.compile(
    r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----"
)
FEISHU_IDENTIFIER = re.compile(
    r"(?<![A-Za-z0-9])(?:cli|ou)_[A-Za-z0-9]{16,}(?![A-Za-z0-9])"
)
PLACEHOLDER_WORDS = ("redacted", "dummy", "changeme", "placeholder", "example", "test-only")


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


def is_placeholder_value(value: str) -> bool:
    normalized = value.strip().strip("'\"").strip().lower()
    return (
        not normalized
        or any(word in normalized for word in PLACEHOLDER_WORDS)
        or (normalized.startswith("<") and normalized.endswith(">"))
        or (normalized.startswith("${") and normalized.endswith("}"))
        or (normalized.startswith("{{") and normalized.endswith("}}"))
        or normalized.startswith("$")
        or re.fullmatch(r"(?:cli_|ou_)?0{8,}", normalized) is not None
    )


def find_likely_secrets(text: str) -> list[str]:
    findings = []
    for match in SECRET_ASSIGNMENT.finditer(text):
        if not is_placeholder_value(match.group("value")):
            findings.append(match.group("name"))
    for match in FEISHU_IDENTIFIER.finditer(text):
        if not is_placeholder_value(match.group(0)):
            findings.append("FEISHU_IDENTIFIER")
    for match in BEARER_TOKEN.finditer(text):
        if not is_placeholder_value(match.group("value")):
            findings.append("BEARER_TOKEN")
    if PRIVATE_KEY_PEM.search(text):
        findings.append("PRIVATE_KEY_PEM")
    return findings


class SecretScannerTests(unittest.TestCase):
    def test_flags_bare_export_yaml_and_prefixed_secrets(self) -> None:
        key_field = "API" + "_KEY"
        app_field = "APP_" + "SECRET"
        credential_field = "PASS" + "WORD"
        vendor_field = "VENDOR_" + key_field
        access_field = "ACCESS_" + "TOKEN"
        refresh_field = "REFRESH_" + "TOKEN"
        client_field = "CLIENT_" + "SECRET"
        service_token_field = "SERVICE_" + "TOKEN"
        service_secret_field = "SERVICE_" + "SECRET"
        identifier = "cli_" + "a1b2c3d4e5f6g7h8"
        pem_header = "-----BEGIN " + "PRIVATE KEY-----"
        bearer = "Bearer " + "eyJhbGciOiJIUzI1Ni.live.signature"
        text = "\n".join(
            (
                f"{key_field}=sk-live-value-123",
                f"export {app_field}=live-app-value-456",
                f'{credential_field}: "live-password-789"',
                f"{vendor_field}: live-vendor-value-012",
                f"{access_field}=live-access-value-345",
                f"{refresh_field}=live-refresh-value-678",
                f"{client_field}=live-client-value-901",
                f"{service_token_field}=live-service-token-234",
                f"{service_secret_field}=live-service-secret-567",
                identifier,
                pem_header,
                bearer,
            )
        )

        self.assertCountEqual(
            [
                key_field,
                app_field,
                credential_field,
                vendor_field,
                access_field,
                refresh_field,
                client_field,
                service_token_field,
                service_secret_field,
                "FEISHU_IDENTIFIER",
                "PRIVATE_KEY_PEM",
                "BEARER_TOKEN",
            ],
            find_likely_secrets(text),
        )

    def test_ignores_documented_placeholders_and_all_zero_ids(self) -> None:
        key_field = "API" + "_KEY"
        app_field = "APP_" + "SECRET"
        credential_field = "PASS" + "WORD"
        access_field = "ACCESS_" + "TOKEN"
        client_field = "CLIENT_" + "SECRET"
        text = "\n".join(
            (
                f"{key_field}=<your-key>",
                f"export {app_field}=redacted",
                f"{credential_field}: dummy-password",
                f"SERVICE_{key_field}=changeme",
                f"SECONDARY_{key_field}=placeholder",
                f"THIRD_{key_field}=" + "${" + key_field + "}",
                f"{access_field}=dummy-token",
                f"{client_field}=" + "${" + client_field + "}",
                "Bearer changeme-placeholder",
                "PRIVATE_KEY=<PRIVATE_KEY_PEM>",
                "FEISHU_APP_ID=cli_" + "0" * 20,
                "ou_" + "0" * 20,
            )
        )

        self.assertEqual([], find_likely_secrets(text))


class SkillPackageTests(unittest.TestCase):
    def test_required_references_are_nonempty_and_cover_key_topics(self) -> None:
        reference_dir = PACKAGE_ROOT / "references"
        for filename, topics in REFERENCE_TOPICS.items():
            with self.subTest(filename=filename):
                path = reference_dir / filename
                self.assertTrue(path.is_file(), f"missing reference: {filename}")
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.strip(), f"empty reference: {filename}")
                for topic in topics:
                    self.assertIn(topic.casefold(), text.casefold(), f"{filename} lacks {topic}")

    def test_operational_references_preserve_reviewed_safety_contracts(self) -> None:
        reference_dir = PACKAGE_ROOT / "references"
        texts = {
            path.name: path.read_text(encoding="utf-8")
            for path in reference_dir.glob("*.md")
        }

        profile = texts["hermes-profile-and-model.md"]
        for marker in ("自动绕过", "--safe-mode", "--toolsets safe", "空白临时 cwd"):
            self.assertIn(marker, profile)
        model_stage = "--stage model <PROFILE_DIR>"
        full_stage = "--stage full <PROFILE_DIR>"
        self.assertIn(model_stage, profile)
        self.assertIn(full_stage, profile)
        self.assertLess(profile.index(model_stage), profile.index(full_stage))
        self.assertIn("省略 `--stage` 默认也是 `full`", profile)

        feishu = texts["feishu-bot-and-permissions.md"]
        for marker in ("im.message.receive_v1", "im:message:send_as_bot", "tmux", "screen"):
            self.assertIn(marker, feishu)
        self.assertNotIn("nohup", feishu.casefold())

        user_auth = texts["lark-user-authorization.md"]
        for marker in ("--scope", "wiki:wiki:readonly", "bitable:app:readonly"):
            self.assertIn(marker, user_auth)
        self.assertIn("不能把 `--domain` 标成只读", user_auth)

        troubleshooting = texts["troubleshooting.md"]
        authorization_refs = {
            "feishu-bot-and-permissions.md": feishu,
            "lark-user-authorization.md": user_auth,
            "troubleshooting.md": troubleshooting,
        }
        for filename, text in authorization_refs.items():
            with self.subTest(url_contract=filename):
                for marker in (
                    "urlsplit",
                    "https",
                    "verification_uri_complete",
                    "userinfo",
                    "`443`",
                    "任何其他端口都拒绝",
                    "accounts.feishu.cn",
                    "accounts.larksuite.com",
                    "open.feishu.cn",
                    "open.larksuite.com",
                    "当前品牌",
                    "精确",
                    "绝不联合放行",
                    "失败关闭",
                    "不可信数据",
                    "hostname 未知",
                    "立即停止",
                    "独立核实",
                    "不转发",
                    "不生成二维码",
                ):
                    self.assertIn(marker, text)
                for mapping in (
                    "`feishu` | `verification_url` / `verification_uri_complete` / `qr_url` | `accounts.feishu.cn`",
                    "`feishu` | `console_url` | `open.feishu.cn`",
                    "`lark` | `verification_url` / `verification_uri_complete` / `qr_url` | `accounts.larksuite.com`",
                    "`lark` | `console_url` | `open.larksuite.com`",
                ):
                    self.assertIn(mapping, text)

        self.assertNotIn("后台运行时同时重定向", troubleshooting)
        for marker in ("tmux", "screen", "保持标准输入", "非交互子命令", "不能套用到交互式 `gateway setup`"):
            self.assertIn(marker, troubleshooting)

        context = texts["context-files-and-prompts.md"]
        for marker in ("动态", "20,000", "保守下限", "只放在 profile 根目录"):
            self.assertIn(marker, context)
        for link in (
            "../scripts/validate_agent_profile.py",
            "../assets/templates/SOUL.md.template",
            "../assets/templates/AGENTS.md.template",
            "../assets/templates/README.md.template",
            "../assets/templates/PROJECT.md.template",
        ):
            self.assertIn(link, context)

        pressure = texts["pressure-scenarios.md"]
        for marker in ("干净环境", "允许工具", "产物证据", "退出码", "至少 2 次", "总体通过门槛"):
            self.assertIn(marker, pressure)
        self.assertIn("`SOUL.md` 只位于 profile 根目录", pressure)
        self.assertNotIn("四类文件位于配置指定的工作目录", pressure)

        for filename, text in texts.items():
            with self.subTest(filename=filename):
                self.assertIn("下一步", text)
                self.assertRegex(text, r"\[[^\]]+\]\([^\)]+\)")

    def test_required_templates_are_nonempty_and_have_role_placeholders(self) -> None:
        template_dir = PACKAGE_ROOT / "assets" / "templates"
        seen_placeholders = set()
        for filename, required in TEMPLATE_PLACEHOLDERS.items():
            with self.subTest(filename=filename):
                path = template_dir / filename
                self.assertTrue(path.is_file(), f"missing template: {filename}")
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.strip(), f"empty template: {filename}")
                self.assertEqual(set(), required - set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
                seen_placeholders.update(re.findall(r"\{\{[A-Z_]+\}\}", text))

        self.assertEqual(ALL_PLACEHOLDERS, seen_placeholders)

    def test_templates_define_single_sources_of_truth(self) -> None:
        template_dir = PACKAGE_ROOT / "assets" / "templates"
        texts = {
            path.name: path.read_text(encoding="utf-8")
            for path in template_dir.glob("*.template")
        }

        ownership = {
            "SOUL.md.template": ("长期人格", "最高底线"),
            "AGENTS.md.template": ("执行流程", "权限边界", "验收规则", "唯一事实来源"),
            "README.md.template": ("能力三分组", "用户入口", "唯一事实来源"),
            "PROJECT.md.template": ("项目目标", "数据流", "文件职责", "总体状态", "唯一事实来源"),
        }
        for filename, markers in ownership.items():
            with self.subTest(filename=filename):
                for marker in markers:
                    self.assertIn(marker, texts[filename])

        placeholder_owners = {
            "{{INPUT_SOURCES}}": "PROJECT.md.template",
            "{{OUTPUT_TARGETS}}": "PROJECT.md.template",
            "{{PERMISSION_BOUNDARIES}}": "AGENTS.md.template",
            "{{VERIFICATION_RULES}}": "AGENTS.md.template",
            "{{AUTOMATIC_CAPABILITIES}}": "README.md.template",
            "{{ON_DEMAND_CAPABILITIES}}": "README.md.template",
            "{{NOT_ENABLED_CAPABILITIES}}": "README.md.template",
        }
        for placeholder, owner in placeholder_owners.items():
            with self.subTest(placeholder=placeholder):
                self.assertIn(placeholder, texts[owner])
                self.assertFalse(
                    any(placeholder in text for filename, text in texts.items() if filename != owner)
                )

        body_owners = {
            "## 服务风格": "SOUL.md.template",
            "## 工具与权限": "AGENTS.md.template",
            "## 验收": "AGENTS.md.template",
            "## 自动运行": "README.md.template",
            "## 按需可用": "README.md.template",
            "## 尚未启用": "README.md.template",
            "填写格式（每项一行）": "README.md.template",
            "## 数据流": "PROJECT.md.template",
            "输入来源：": "PROJECT.md.template",
            "输出目标：": "PROJECT.md.template",
            "## 总体状态": "PROJECT.md.template",
        }
        for marker, owner in body_owners.items():
            with self.subTest(marker=marker):
                locations = [filename for filename, text in texts.items() if marker in text]
                self.assertEqual([owner], locations)

    def test_templates_distinguish_continuing_and_new_authorization(self) -> None:
        template_dir = PACKAGE_ROOT / "assets" / "templates"
        texts = {
            path.name: path.read_text(encoding="utf-8")
            for path in template_dir.glob("*.template")
        }
        agents = texts["AGENTS.md.template"]
        full_rule_markers = (
            "目标、范围、频率固定",
            "可直接执行",
            "新增任务",
            "改变范围、频率或接收人",
            "超出授权边界",
            "高风险写入、删除、权限变更",
            "必须先确认对象、范围与后果",
        )
        for marker in full_rule_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, agents)
                self.assertEqual(1, sum(text.count(marker) for text in texts.values()))

        for filename in ("SOUL.md.template", "README.md.template", "PROJECT.md.template"):
            with self.subTest(filename=filename):
                text = texts[filename]
                for marker in ("权限、持续授权和事故处置", "AGENTS.md", "唯一事实来源", "本文件不重复"):
                    self.assertIn(marker, text)

    def test_readme_capability_entries_require_operational_fields(self) -> None:
        text = (PACKAGE_ROOT / "assets" / "templates" / "README.md.template").read_text(
            encoding="utf-8"
        )
        headings = ("自动运行", "按需可用", "尚未启用")
        required_fields = ("触发条件", "输入", "输出", "运行身份/权限", "最近验证证据")
        for heading in headings:
            start = text.index(f"## {heading}")
            end = text.find("\n## ", start + 1)
            section = text[start:] if end == -1 else text[start:end]
            with self.subTest(heading=heading):
                for field in required_fields:
                    self.assertIn(field, section)
                if heading == "尚未启用":
                    self.assertIn("启用条件", section)

    def test_templates_cover_service_style_and_sensitive_log_cleanup(self) -> None:
        template_dir = PACKAGE_ROOT / "assets" / "templates"
        soul = (template_dir / "SOUL.md.template").read_text(encoding="utf-8")
        agents = (template_dir / "AGENTS.md.template").read_text(encoding="utf-8")

        for marker in ("可编辑", "结论先行", "表达简洁", "一次只问一个", "阻塞"):
            self.assertIn(marker, soul)
        for marker in (
            "疑似泄露",
            "停止使用相关凭据",
            "清理或脱敏",
            "密钥",
            "令牌",
            "临时授权",
            "日志与临时材料",
            "通知负责人",
            "已有预授权的事故响应流程",
            "自动轮换或吊销",
            "否则必须先确认",
        ):
            self.assertIn(marker, agents)

    def test_project_requires_a_concrete_overall_status(self) -> None:
        project = (
            PACKAGE_ROOT / "assets" / "templates" / "PROJECT.md.template"
        ).read_text(encoding="utf-8")

        for marker in ("档案与模型", "飞书连接", "自动任务", "最近验证日期", "未决风险"):
            self.assertIn(marker, project)
        self.assertIn("具体能力明细只在 `README.md` 更新", project)

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
        offenders = []
        for path in self._package_text_files(exclude_tests=True):
            if find_likely_secrets(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(PACKAGE_ROOT).as_posix())

        self.assertEqual([], offenders)

    @staticmethod
    def _package_text_files(*, exclude_tests: bool = False) -> list[Path]:
        return sorted(
            path
            for path in PACKAGE_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".template"}
            and not (exclude_tests and "tests" in path.relative_to(PACKAGE_ROOT).parts)
        )


if __name__ == "__main__":
    unittest.main()
