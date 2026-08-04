import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE_ROOT / "scripts" / "validate_agent_profile.py"
WORKSPACE_CONTEXT_FILES = ("AGENTS.md", "README.md", "PROJECT.md")
REQUIRED_FEISHU_ENV = {
    "FEISHU_APP_ID": "cli_fixture_7f3a9c",
    "FEISHU_APP_SECRET": "synthetic-secret-8d21f6",
    "FEISHU_DOMAIN": "feishu",
    "FEISHU_CONNECTION_MODE": "websocket",
    "FEISHU_ALLOWED_USERS": "ou_fixture_4e91bd",
    "FEISHU_GROUP_POLICY": "allowlist",
    "FEISHU_REQUIRE_MENTION": "true",
}


def run_validator(
    profile: Path,
    stage: str | None = None,
    runtime_cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    if stage is not None:
        command.extend(("--stage", stage))
    if runtime_cwd is not None:
        command.extend(("--runtime-cwd", str(runtime_cwd)))
    command.append(str(profile))
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except subprocess.TimeoutExpired as error:
        raise AssertionError(
            f"validator exceeded the 10-second timeout for {profile}"
        ) from error


class ValidateAgentProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.profile = Path(self.temp_dir.name) / "test-agent"
        self.workspace = self.profile / "workspace"
        self._write_complete_profile()

    def _write_complete_profile(self) -> None:
        self.profile.mkdir()
        self.workspace.mkdir()
        for directory in ("skills", "sessions", "memories"):
            (self.profile / directory).mkdir()

        (self.profile / "profile.yaml").write_text(
            "name: test-agent\ndisplay_name: Test Agent\nstatus: active\n",
            encoding="utf-8",
        )
        (self.profile / "config.yaml").write_text(
            "\n".join(
                (
                    "model:",
                    "  default: MiniMax-M3",
                    "  provider: custom:minimax",
                    "providers:",
                    "  minimax:",
                    "    base_url: https://api.example.invalid/v1",
                    "    key_env: MINIMAX_M3_API_KEY",
                    "    api_mode: chat_completions",
                    "terminal:",
                    f"  cwd: {self.workspace.as_posix()}",
                    "",
                )
            ),
            encoding="utf-8",
        )
        (self.profile / ".env").write_text(
            "\n".join(
                ["MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a"]
                + [f"{name}={value}" for name, value in REQUIRED_FEISHU_ENV.items()]
                + [""]
            ),
            encoding="utf-8",
        )
        (self.profile / "SOUL.md").write_text("# Test Agent\n", encoding="utf-8")
        for filename in WORKSPACE_CONTEXT_FILES:
            (self.workspace / filename).write_text(
                f"# {filename}\nTest context.\n", encoding="utf-8"
            )

    @staticmethod
    def _output(result: subprocess.CompletedProcess[str]) -> str:
        return f"{result.stdout}\n{result.stderr}"

    def test_complete_profile_passes(self) -> None:
        result = run_validator(self.profile)

        self.assertEqual(0, result.returncode, self._output(result))

    def test_model_stage_allows_pre_app_profile_but_full_rejects_it(self) -> None:
        env_path = self.profile / ".env"
        env_path.write_text(
            "MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a\n",
            encoding="utf-8",
        )
        (self.profile / "SOUL.md").unlink()
        for filename in WORKSPACE_CONTEXT_FILES:
            (self.workspace / filename).unlink()

        model_result = run_validator(self.profile, stage="model")
        full_result = run_validator(self.profile, stage="full")
        default_result = run_validator(self.profile)

        self.assertEqual(0, model_result.returncode, self._output(model_result))
        self.assertNotEqual(0, full_result.returncode)
        self.assertEqual(full_result.returncode, default_result.returncode)
        self.assertEqual(full_result.stdout, default_result.stdout)

    def test_cli_help_documents_validation_stages(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        output = self._output(result).lower()
        self.assertEqual(0, result.returncode, output)
        self.assertIn("--stage", output)
        self.assertIn("model", output)
        self.assertIn("full", output)

    def test_full_stage_rejects_obvious_env_placeholders_without_echoing(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        cases = {
            "MINIMAX_M3_API_KEY": "<model-key>",
            "FEISHU_APP_ID": "your-app-id",
            "FEISHU_APP_SECRET": "changeme-secret",
            "FEISHU_ALLOWED_USERS": "0000000000",
        }
        for name, placeholder in cases.items():
            with self.subTest(name=name):
                lines = [
                    f"{name}={placeholder}" if line.startswith(f"{name}=") else line
                    for line in original.splitlines()
                ]
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(name, output)
                self.assertNotIn(placeholder, output)
        env_path.write_text(original, encoding="utf-8")

    def test_model_stage_rejects_model_key_placeholders_without_echoing(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        for placeholder in ("<model-key>", "changeme-model-key", "redacted-key"):
            with self.subTest(placeholder=placeholder):
                env_path.write_text(
                    original.replace(
                        "MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a",
                        f"MINIMAX_M3_API_KEY={placeholder}",
                    ),
                    encoding="utf-8",
                )
                result = run_validator(self.profile, stage="model")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("MINIMAX_M3_API_KEY", output)
                self.assertNotIn(placeholder, output)
        env_path.write_text(original, encoding="utf-8")

    def test_model_stage_rejects_xxx_segment_without_false_positive(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        placeholder = "sk-xxx"
        env_path.write_text(
            original.replace(
                "MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a",
                f"MINIMAX_M3_API_KEY={placeholder}",
            ),
            encoding="utf-8",
        )
        result = run_validator(self.profile, stage="model")
        output = self._output(result)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MINIMAX_M3_API_KEY", output)
        self.assertNotIn(placeholder, output)

        env_path.write_text(
            original.replace(
                "MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a",
                "MINIMAX_M3_API_KEY=sk-exxxample-valid",
            ),
            encoding="utf-8",
        )
        valid_result = run_validator(self.profile, stage="model")
        self.assertEqual(0, valid_result.returncode, self._output(valid_result))

    def test_unresolved_variable_templates_are_rejected_without_echoing(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        model_templates = (
            "${MODEL_KEY}",
            "$MODEL_KEY",
            "{{MODEL_KEY}}",
            "%MODEL_KEY%",
            "$(MODEL_KEY)",
        )
        for template in model_templates:
            with self.subTest(stage="model", template=template):
                env_path.write_text(
                    original.replace(
                        "MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a",
                        f"MINIMAX_M3_API_KEY={template}",
                    ),
                    encoding="utf-8",
                )
                result = run_validator(self.profile, stage="model")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("MINIMAX_M3_API_KEY", output)
                self.assertNotIn(template, output)

        for name, template in (
            ("FEISHU_APP_ID", "${APP_ID}"),
            ("FEISHU_APP_SECRET", "$APP_SECRET"),
            ("FEISHU_ALLOWED_USERS", "{{ALLOWED_USERS}}"),
        ):
            with self.subTest(stage="full", name=name):
                lines = [
                    f"{name}={template}" if line.startswith(f"{name}=") else line
                    for line in original.splitlines()
                ]
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(name, output)
                self.assertNotIn(template, output)

        env_path.write_text(
            original.replace(
                "MINIMAX_M3_API_KEY=synthetic-model-key-3c8f2a",
                "MINIMAX_M3_API_KEY=sk-literal-$-braces-valid-7a2c",
            ),
            encoding="utf-8",
        )
        normal_result = run_validator(self.profile, stage="model")
        self.assertEqual(0, normal_result.returncode, self._output(normal_result))

    def test_full_stage_rejects_xxx_feishu_placeholders_without_echoing(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        cases = {
            "FEISHU_APP_ID": "cli_xxx",
            "FEISHU_APP_SECRET": "secret_xxx",
            "FEISHU_ALLOWED_USERS": "ou_xxx",
        }
        for name, placeholder in cases.items():
            with self.subTest(name=name):
                lines = [
                    f"{name}={placeholder}" if line.startswith(f"{name}=") else line
                    for line in original.splitlines()
                ]
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(name, output)
                self.assertNotIn(placeholder, output)
        env_path.write_text(original, encoding="utf-8")

    def test_approvals_off_fails_while_safe_modes_pass(self) -> None:
        config_path = self.profile / "config.yaml"
        original = config_path.read_text(encoding="utf-8")
        for mode, should_pass in (("off", False), ("smart", True), ("manual", True)):
            with self.subTest(mode=mode):
                config_path.write_text(
                    original + f"approvals:\n  mode: {mode}\n", encoding="utf-8"
                )
                result = run_validator(self.profile)
                if should_pass:
                    self.assertEqual(0, result.returncode, self._output(result))
                else:
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("APPROVAL", self._output(result).upper())
        config_path.write_text(original, encoding="utf-8")

    def test_profile_yaml_must_parse_and_match_directory_name(self) -> None:
        profile_path = self.profile / "profile.yaml"
        cases = (
            ("name: [unterminated\nstatus: active\n", "PROFILE_INVALID"),
            ("name: another-agent\nstatus: active\n", "PROFILE_NAME"),
            ("name: test-agent\nstatus:\n", "PROFILE_STATUS"),
        )
        for content, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                profile_path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected_code, self._output(result))

    def test_inactive_profile_status_warns_without_failing(self) -> None:
        (self.profile / "profile.yaml").write_text(
            "name: test-agent\nstatus: inactive\n", encoding="utf-8"
        )
        result = run_validator(self.profile)
        output = self._output(result)
        self.assertEqual(0, result.returncode, output)
        self.assertIn("WARN", output.upper())
        self.assertIn("PROFILE_STATUS", output)

    def test_legacy_description_only_profile_uses_implicit_identity(self) -> None:
        # Older Hermes profiles (including the deployed wxagent fixture) store
        # only description metadata; their directory name and active presence
        # are the effective identity/status.
        (self.profile / "profile.yaml").write_text(
            "description: Synthetic legacy profile\n"
            "description_auto: false\n",
            encoding="utf-8",
        )
        result = run_validator(self.profile)
        self.assertEqual(0, result.returncode, self._output(result))

    def test_current_hermes_implicit_profile_metadata_shapes_pass(self) -> None:
        # Current Hermes profile loading treats a missing/empty metadata file,
        # or description-only metadata, as directory identity + active status.
        profile_path = self.profile / "profile.yaml"
        cases = (None, "", "{}\n", "description: ''\ndescription_auto: false\n")
        for content in cases:
            with self.subTest(content=repr(content)):
                if content is None:
                    profile_path.unlink(missing_ok=True)
                else:
                    profile_path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile)
                self.assertEqual(0, result.returncode, self._output(result))

    def test_block_scalars_in_unknown_and_smart_policy_sections_pass(self) -> None:
        config_path = self.profile / "config.yaml"
        config_path.write_text(
            config_path.read_text(encoding="utf-8")
            + "approvals:\n"
            + "  mode: smart\n"
            + '  "smart_policy": |2-\n'
            + "    Require review for destructive commands.\n"
            + "    Allow read-only checks.\n"
            + "unknown_notes: >-2\n"
            + "  First folded line.\n"
            + "  Second folded line.\n"
            + "unknown_literal: |2\n"
            + "  Explicit indentation.\n",
            encoding="utf-8",
        )
        result = run_validator(self.profile)
        self.assertEqual(0, result.returncode, self._output(result))

    def test_each_context_location_rejects_secret_without_echoing(self) -> None:
        locations = (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        )
        for path in locations:
            with self.subTest(path=path.name):
                secret = "actual-" + "credential-a1b2c3d4"
                path.write_text("API" + f"_KEY={secret}\n", encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(path.name, output)
                self.assertIn("CREDENTIAL", output)
                self.assertNotIn(secret, output)
                path.write_text(f"# {path.name}\nSafe context.\n", encoding="utf-8")

    def test_context_bare_token_and_secret_assignments_are_detected(self) -> None:
        locations = (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        )
        for name in ("TOKEN", "SECRET"):
            value = "live_7a2c9f4e8b1d6c3f"
            for path in locations:
                with self.subTest(name=name, path=path.name):
                    content = f"{name}={value}\n"
                    path.write_text(content, encoding="utf-8")
                    result = run_validator(self.profile, stage="full")
                    output = self._output(result)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("CREDENTIAL", output)
                    self.assertNotIn(value, output)
                    path.write_text(f"# {path.name}\nSafe context.\n", encoding="utf-8")

    def test_context_assignments_report_short_nonplaceholder_values(self) -> None:
        cases = (
            ("TOKEN=abc123\n", "abc123"),
            ("ACCESS_TOKEN=abc+/def==\n", "abc+/def=="),
        )
        path = self.profile / "SOUL.md"
        for content, value in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("CREDENTIAL", output)
                self.assertNotIn(value, output)

    def test_context_prefixed_uppercase_assignments_are_detected(self) -> None:
        cases = (
            ("the TOKEN=live_secret_123\n", "live_secret_123"),
            ("your TOKEN=live_secret_123\n", "live_secret_123"),
            ("security SECRET=live_secret_123\n", "live_secret_123"),
        )
        path = self.profile / "SOUL.md"
        for content, value in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("CREDENTIAL", output)
                self.assertNotIn(value, output)

    def test_context_natural_security_terms_without_assignment_are_ignored(self) -> None:
        content = (
            "The TOKEN is a credential name.\n"
            "Security SECRET guidance belongs in the policy.\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")

        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_case_insensitive_assignments_and_json_keys_are_detected(self) -> None:
        cases = (
            ("access_token=live_secret_123\n", "live_secret_123"),
            ('{"access_token":"live_secret_123"}\n', "live_secret_123"),
            ('{"secret": "abc123"}\n', "abc123"),
        )
        path = self.profile / "SOUL.md"
        for content, value in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("CREDENTIAL", output)
                self.assertNotIn(value, output)

    def test_context_unquoted_colon_explanations_are_ignored(self) -> None:
        content = (
            "TOKEN: used for authentication.\n"
            "access_token: a field name in documentation.\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")

        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_yaml_colon_credential_shapes_are_detected(self) -> None:
        cases = (
            ("ACCESS_TOKEN: live_secret_abc123\n", "live_secret_abc123"),
            ("API_KEY: sk-live-abc123\n", "sk-live-abc123"),
        )
        path = self.profile / "SOUL.md"
        for content, value in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("CREDENTIAL", output)
                self.assertNotIn(value, output)

    def test_context_yaml_colon_credential_explanations_are_ignored(self) -> None:
        content = (
            "TOKEN: used for authentication\n"
            "SECRET: used for policy text\n"
            "API_KEY: required\n"
            "ACCESS_TOKEN: optional\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")

        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_bearer_and_private_key_categories_are_rejected(self) -> None:
        path = self.profile / "SOUL.md"
        cases = (
            ("Authorization: Bearer " + "eyJfixture.payload.signature", "BEARER"),
            ("-----BEGIN " + "PRIVATE KEY-----\nfixture\n", "PRIVATE_KEY"),
        )
        for content, category in cases:
            with self.subTest(category=category):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(category, output)
                self.assertNotIn(content.splitlines()[0], output)

    def test_context_documentation_placeholders_are_not_secrets(self) -> None:
        safe_documentation = (
            "API_KEY=${API_KEY}\n"
            "APP_SECRET=<redacted>\n"
            "ACCESS_TOKEN={{ACCESS_TOKEN}}\n"
            "REFRESH_TOKEN=$REFRESH_TOKEN\n"
            "CLIENT_SECRET=dummy\n"
            "PASSWORD=changeme\n"
            "Authorization: Bearer <token>\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(safe_documentation, encoding="utf-8")
        result = run_validator(self.profile, stage="full")
        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_natural_language_security_terms_are_not_secrets(self) -> None:
        safe_prose = (
            "The access token: expires after one hour.\n"
            "Bearer authentication is described in the security guide.\n"
            "The client secret: should be rotated by an administrator.\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(safe_prose, encoding="utf-8")
        result = run_validator(self.profile, stage="full")
        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_structured_secret_forms_are_detected_without_echoing(self) -> None:
        values = {
            self.profile / "SOUL.md": (
                "| API_KEY | " + "sk-live-7a2c9f4e8b1d" + " |\n",
                "CREDENTIAL",
            ),
            self.workspace / "AGENTS.md": (
                "https://example.invalid/device?device_code="
                + "ABCD-EFGH-7K2M"
                + "\n",
                "AUTHORIZATION_CODE",
            ),
            self.workspace / "README.md": (
                "Application: " + "cli_a1b2c3d4e5f6g7h8" + "\n",
                "FEISHU_APP_ID",
            ),
            self.workspace / "PROJECT.md": (
                "Owner: " + "ou_a1b2c3d4e5f6g7h8i9j0" + "\n",
                "FEISHU_OPEN_ID",
            ),
        }
        for path, (content, category) in values.items():
            with self.subTest(path=path.name, category=category):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(path.name, output)
                self.assertIn(category, output)
                self.assertNotIn(content.strip(), output)
                path.write_text(f"# {path.name}\nSafe context.\n", encoding="utf-8")

    def test_context_credential_tables_ignore_labels_and_placeholders(self) -> None:
        safe_table = (
            "| API_KEY | required |\n"
            "| ACCESS_TOKEN | optional |\n"
            "| APP_SECRET | <...> |\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(safe_table, encoding="utf-8")

        result = run_validator(self.profile, stage="full")

        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_credential_tables_flag_short_obvious_passwords(self) -> None:
        value = "passw0rd"
        content = f"| PASSWORD | {value} |\n"
        path = self.profile / "SOUL.md"
        path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("CREDENTIAL", output)
        self.assertNotIn(value, output)

    def test_context_credential_tables_flag_short_nonplaceholder_values(self) -> None:
        value = "liveTokenABC123"
        content = f"| ACCESS_TOKEN | {value} |\n"
        path = self.profile / "SOUL.md"
        path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("CREDENTIAL", output)
        self.assertNotIn(value, output)

    def test_context_credential_tables_ignore_explicit_labels(self) -> None:
        content = (
            "| API_KEY | required |\n"
            "| ACCESS_TOKEN | optional |\n"
            "| APP_SECRET | example |\n"
            "| TOKEN | placeholder |\n"
            "| SECRET | redacted |\n"
            "| PASSWORD | none |\n"
            "| PASSWORD | unset |\n"
            "| PASSWORD | name |\n"
            "| PASSWORD | value |\n"
            "| PASSWORD | environment variable |\n"
            "| PASSWORD | 填写 |\n"
            "| PASSWORD | 待填 |\n"
            "| PASSWORD | <...> |\n"
            "| PASSWORD | $VAR |\n"
            "| PASSWORD | {{PASSWORD}} |\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")

        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_authorization_code_accepts_letter_only_device_codes(self) -> None:
        cases = (
            "https://example.invalid/device?code=ABCD-EFGH-IJKL\n",
            "https://example.invalid/device?device_code=ABCD_EFGH.IJKL\n",
        )
        for content in cases:
            with self.subTest(content=content):
                path = self.workspace / "AGENTS.md"
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("AUTHORIZATION_CODE", output)
                self.assertNotIn(content.strip(), output)

    def test_context_authorization_code_ignores_plain_english_query_values(self) -> None:
        safe_content = "https://example.invalid/device?code=this-is-a-code\n"
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(safe_content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")

        self.assertEqual(0, result.returncode, self._output(result))

    def test_context_sensitive_url_query_values_are_detected_without_echoing(self) -> None:
        cases = (
            ("token", "live_7a2c9f4e8b1d6c3f"),
            ("access_token", "live_7a2c9f4e8b1d6c3f"),
            ("refresh_token", "live_7a2c9f4e8b1d6c3f"),
            ("secret", "live_7a2c9f4e8b1d6c3f"),
            ("key", "live_7a2c9f4e8b1d6c3f"),
        )
        path = self.workspace / "AGENTS.md"
        for name, value in cases:
            with self.subTest(name=name):
                content = f"https://example.invalid/callback?{name}={value}\n"
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("CREDENTIAL", output)
                self.assertNotIn(value, output)

    def test_context_sensitive_url_fragments_are_detected_without_echoing(self) -> None:
        cases = (
            (
                "https://example.invalid/callback#access_token=live_7a2c9f4e8b1d6c3f\n",
                "CREDENTIAL",
                "live_7a2c9f4e8b1d6c3f",
            ),
            (
                "https://example.invalid/callback#code=ABCD-EFGH-IJKL\n",
                "AUTHORIZATION_CODE",
                "ABCD-EFGH-IJKL",
            ),
        )
        path = self.workspace / "README.md"
        for content, category, value in cases:
            with self.subTest(category=category):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(category, output)
                self.assertNotIn(value, output)

    def test_context_sensitive_url_reports_short_nonplaceholder_values(self) -> None:
        content = "https://example.invalid/callback?token=abc123\n"
        path = self.workspace / "AGENTS.md"
        path.write_text(content, encoding="utf-8")

        result = run_validator(self.profile, stage="full")
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("CREDENTIAL", output)
        self.assertNotIn("abc123", output)

    def test_context_sensitive_url_detects_lowercase_authorization_codes(self) -> None:
        cases = (
            ("https://example.invalid/callback?code=abcdefghi\n", "abcdefghi"),
            ("https://example.invalid/callback#device_code=abcdefghi\n", "abcdefghi"),
        )
        path = self.workspace / "AGENTS.md"
        for content, value in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("AUTHORIZATION_CODE", output)
                self.assertNotIn(value, output)

    def test_context_sensitive_url_ignores_short_words_and_examples(self) -> None:
        cases = (
            "https://example.invalid/callback?code=short\n",
            "https://example.invalid/callback?code=example-code\n",
            "https://example.invalid/callback?code=authorization-code\n",
            "https://example.invalid/callback?code=this-is-a-code\n",
        )
        path = self.workspace / "AGENTS.md"
        for content in cases:
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                result = run_validator(self.profile, stage="full")
                self.assertEqual(0, result.returncode, self._output(result))

    def test_context_id_and_url_placeholders_are_not_secrets(self) -> None:
        safe_values = (
            "| ACCESS_TOKEN | ${ACCESS_TOKEN} |\n"
            "https://example.invalid/device?user_code=XXXX-XXXX\n"
            "Application: cli_xxx\n"
            "Owner: ou_000000000000\n"
            "Bearer authentication remains documentation only.\n"
        )
        for path in (self.profile / "SOUL.md",) + tuple(
            self.workspace / filename for filename in WORKSPACE_CONTEXT_FILES
        ):
            path.write_text(safe_values, encoding="utf-8")
        result = run_validator(self.profile, stage="full")
        self.assertEqual(0, result.returncode, self._output(result))

    def test_unrelated_flow_collections_and_mapping_lists_are_tolerated(self) -> None:
        config_path = self.profile / "config.yaml"
        config_path.write_text(
            config_path.read_text(encoding="utf-8")
            + 'extra: {"name":"first"}\n'
            + "extra_list: [one, two]\n"
            + "unknown_section:\n"
            + "  - name: first\n"
            + "    enabled: true\n"
            + "  - \"name\": second\n"
            + "  -\n"
            + "    name: nested\n"
            + "  - metadata:\n"
            + "      owner: synthetic\n"
            + "    name: third\n",
            encoding="utf-8",
        )
        result = run_validator(self.profile)
        self.assertEqual(0, result.returncode, self._output(result))

    def test_complete_profile_with_block_lists_passes(self) -> None:
        config_path = self.profile / "config.yaml"
        content = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            content
            + "toolsets:\n"
            + "  - terminal\n"
            + "approvals:\n"
            + "  deny:\n"
            + "    - '*rm -rf*'\n",
            encoding="utf-8",
        )

        result = run_validator(self.profile)

        self.assertEqual(0, result.returncode, self._output(result))

    def test_missing_required_file_fails(self) -> None:
        (self.profile / "config.yaml").unlink()

        result = run_validator(self.profile)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("config.yaml", self._output(result))

    def test_malformed_yaml_fails(self) -> None:
        (self.profile / "config.yaml").write_text(
            "model: [unterminated\n", encoding="utf-8"
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertTrue("config.yaml" in output or "yaml" in output.lower())

    def test_unknown_provider_reference_fails(self) -> None:
        config_path = self.profile / "config.yaml"
        content = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            content.replace("custom:minimax", "custom:missing-provider"),
            encoding="utf-8",
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing-provider", output)

    def test_mismatched_key_env_fails_without_printing_secret(self) -> None:
        secret = "fixture-secret-must-not-appear"
        (self.profile / ".env").write_text(
            f"WRONG_MODEL_KEY={secret}\n"
            "FEISHU_APP_ID=cli_fixture_7f3a9c\n"
            "FEISHU_APP_SECRET=synthetic-secret-8d21f6\n"
            "FEISHU_DOMAIN=feishu\n"
            "FEISHU_CONNECTION_MODE=websocket\n"
            "FEISHU_ALLOWED_USERS=ou_fixture_4e91bd\n"
            "FEISHU_GROUP_POLICY=allowlist\n"
            "FEISHU_REQUIRE_MENTION=true\n",
            encoding="utf-8",
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("MINIMAX_M3_API_KEY", output)
        self.assertNotIn(secret, output)

    def test_required_secret_and_identity_values_must_not_be_blank(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        names = (
            "MINIMAX_M3_API_KEY",
            "FEISHU_APP_ID",
            "FEISHU_APP_SECRET",
            "FEISHU_ALLOWED_USERS",
        )
        for name in names:
            for blank in ("", "   "):
                with self.subTest(name=name, blank=repr(blank)):
                    lines = []
                    for line in original.splitlines():
                        if line.startswith(f"{name}="):
                            lines.append(f"{name}={blank}")
                        else:
                            lines.append(line)
                    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    result = run_validator(self.profile)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn(name, self._output(result))
        env_path.write_text(original, encoding="utf-8")

    def test_dotenv_export_quotes_comments_and_hashes_are_supported(self) -> None:
        secret_values = (
            "model#secret",
            "cli#app-id",
            "app#secret",
            "ou#allowed-user",
        )
        (self.profile / ".env").write_text(
            "export MINIMAX_M3_API_KEY=\"model#secret\" # model comment\n"
            "FEISHU_APP_ID='cli#app-id' # id comment\n"
            "export FEISHU_APP_SECRET=\"app#secret\" # secret comment\n"
            "FEISHU_DOMAIN='feishu' # domain comment\n"
            "FEISHU_CONNECTION_MODE=\"websocket\" # mode comment\n"
            "export FEISHU_ALLOWED_USERS='ou#allowed-user' # user comment\n"
            "FEISHU_GROUP_POLICY=allowlist # policy comment\n"
            "FEISHU_REQUIRE_MENTION=true # mention comment\n",
            encoding="utf-8",
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertEqual(0, result.returncode, output)
        for secret in secret_values:
            self.assertNotIn(secret, output)

    def test_builtin_provider_without_provider_mapping_does_not_fail(self) -> None:
        config_path = self.profile / "config.yaml"
        content = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            content.replace("custom:minimax", "openrouter"), encoding="utf-8"
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertEqual(0, result.returncode, output)
        self.assertIn("WARN", output.upper())
        self.assertNotIn("PROVIDER_UNKNOWN", output)

    def test_runtime_registry_providers_without_mappings_do_not_fail(self) -> None:
        config_path = self.profile / "config.yaml"
        original = config_path.read_text(encoding="utf-8")
        for provider in ("openai-api", "anthropic", "xai-oauth"):
            with self.subTest(provider=provider):
                config_path.write_text(
                    original.replace("custom:minimax", provider), encoding="utf-8"
                )
                result = run_validator(self.profile)
                output = self._output(result)
                self.assertEqual(0, result.returncode, output)
                self.assertIn("WARN", output.upper())
                self.assertNotIn("PROVIDER_UNKNOWN", output)
        config_path.write_text(original, encoding="utf-8")

    def test_unknown_non_custom_provider_fails(self) -> None:
        config_path = self.profile / "config.yaml"
        content = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            content.replace("custom:minimax", "definitely-not-a-provider"),
            encoding="utf-8",
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("PROVIDER_UNKNOWN", output)

    def test_missing_workspace_fails(self) -> None:
        for path in self.workspace.iterdir():
            path.unlink()
        self.workspace.rmdir()

        result = run_validator(self.profile)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("workspace", self._output(result).lower())

    def test_runtime_cwd_placeholders_warn_in_model_but_fail_unresolved_full(self) -> None:
        config_path = self.profile / "config.yaml"
        original = config_path.read_text(encoding="utf-8")
        for placeholder in ("auto", "cwd", "."):
            with self.subTest(placeholder=placeholder):
                config_path.write_text(
                    original.replace(self.workspace.as_posix(), placeholder),
                    encoding="utf-8",
                )
                model_result = run_validator(self.profile, stage="model")
                full_result = run_validator(self.profile, stage="full")
                self.assertEqual(
                    0, model_result.returncode, self._output(model_result)
                )
                self.assertIn("WARN", self._output(model_result).upper())
                self.assertNotEqual(0, full_result.returncode)
                self.assertIn("WORKSPACE_UNRESOLVED", self._output(full_result))
        config_path.write_text(original, encoding="utf-8")

    def test_runtime_cwd_resolves_placeholder_for_full_context_check(self) -> None:
        config_path = self.profile / "config.yaml"
        content = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            content.replace(self.workspace.as_posix(), "cwd"), encoding="utf-8"
        )

        result = run_validator(
            self.profile, stage="full", runtime_cwd=self.workspace
        )

        self.assertEqual(0, result.returncode, self._output(result))

    def test_uppercase_cwd_placeholders_are_invalid_relative_paths(self) -> None:
        config_path = self.profile / "config.yaml"
        original = config_path.read_text(encoding="utf-8")
        for invalid_placeholder in ("AUTO", "CWD"):
            with self.subTest(invalid_placeholder=invalid_placeholder):
                config_path.write_text(
                    original.replace(
                        self.workspace.as_posix(), invalid_placeholder
                    ),
                    encoding="utf-8",
                )
                result = run_validator(self.profile)
                output = self._output(result)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("WORKSPACE_RELATIVE", output)
        config_path.write_text(original, encoding="utf-8")

    def test_ordinary_relative_cwd_fails_instead_of_using_profile(self) -> None:
        config_path = self.profile / "config.yaml"
        content = config_path.read_text(encoding="utf-8")
        config_path.write_text(
            content.replace(self.workspace.as_posix(), "workspace"), encoding="utf-8"
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("relative", output.lower())

    def test_windows_and_posix_absolute_cwd_formats_are_recognized(self) -> None:
        config_path = self.profile / "config.yaml"
        original = config_path.read_text(encoding="utf-8")
        formats = (
            (r"Z:\definitely-missing-agentgo-workspace", os.name == "nt"),
            ("/definitely-missing-agentgo-workspace", os.name != "nt"),
        )
        for cwd, native_format in formats:
            with self.subTest(cwd=cwd):
                config_path.write_text(
                    original.replace(self.workspace.as_posix(), cwd), encoding="utf-8"
                )
                full_result = run_validator(self.profile, stage="full")
                full_output = self._output(full_result)
                self.assertNotEqual(0, full_result.returncode)
                self.assertNotIn("relative", full_output.lower())
                if not native_format:
                    model_result = run_validator(self.profile, stage="model")
                    model_output = self._output(model_result)
                    self.assertEqual(0, model_result.returncode, model_output)
                    self.assertIn("WARN", model_output.upper())
        config_path.write_text(original, encoding="utf-8")

    def test_each_missing_context_file_fails(self) -> None:
        for filename in WORKSPACE_CONTEXT_FILES:
            with self.subTest(filename=filename):
                path = self.workspace / filename
                original = path.read_text(encoding="utf-8")
                path.unlink()
                try:
                    result = run_validator(self.profile)
                finally:
                    path.write_text(original, encoding="utf-8")

                self.assertNotEqual(0, result.returncode)
                self.assertIn(filename, self._output(result))

    def test_missing_root_soul_file_fails(self) -> None:
        (self.profile / "SOUL.md").unlink()

        result = run_validator(self.profile)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("SOUL.md", self._output(result))

    def test_context_files_in_wrong_locations_fail(self) -> None:
        cases = (
            (self.profile / "SOUL.md", self.workspace / "SOUL.md"),
            (self.workspace / "AGENTS.md", self.profile / "AGENTS.md"),
        )
        for expected_path, wrong_path in cases:
            with self.subTest(filename=expected_path.name):
                self.assertFalse(wrong_path.exists(), f"fixture collision: {wrong_path}")
                expected_path.replace(wrong_path)
                try:
                    result = run_validator(self.profile)
                finally:
                    wrong_path.replace(expected_path)

                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected_path.name, self._output(result))

    def test_oversized_context_file_warns(self) -> None:
        (self.workspace / "AGENTS.md").write_text("界" * 20_001, encoding="utf-8")

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertEqual(0, result.returncode, output)
        self.assertIn("WARN", output.upper())
        self.assertIn("AGENTS.md", output)

    def test_invalid_feishu_policy_fails(self) -> None:
        env_path = self.profile / ".env"
        content = env_path.read_text(encoding="utf-8")
        env_path.write_text(
            content.replace("FEISHU_GROUP_POLICY=allowlist", "FEISHU_GROUP_POLICY=everyone"),
            encoding="utf-8",
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("FEISHU_GROUP_POLICY", output)
        self.assertNotIn("everyone", output)

    def test_each_required_feishu_variable_must_be_present(self) -> None:
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        for name in REQUIRED_FEISHU_ENV:
            with self.subTest(name=name):
                env_path.write_text(
                    "\n".join(
                        line
                        for line in original.splitlines()
                        if not line.startswith(f"{name}=")
                    )
                    + "\n",
                    encoding="utf-8",
                )
                try:
                    result = run_validator(self.profile)
                finally:
                    env_path.write_text(original, encoding="utf-8")

                self.assertNotEqual(0, result.returncode)
                self.assertIn(name, self._output(result))

    def test_invalid_feishu_settings_fail(self) -> None:
        invalid_settings = {
            "FEISHU_DOMAIN": ("feishu", "example-domain"),
            "FEISHU_CONNECTION_MODE": ("websocket", "polling"),
            "FEISHU_REQUIRE_MENTION": ("true", "sometimes"),
        }
        env_path = self.profile / ".env"
        original = env_path.read_text(encoding="utf-8")
        for name, (valid, invalid) in invalid_settings.items():
            with self.subTest(name=name):
                env_path.write_text(
                    original.replace(f"{name}={valid}", f"{name}={invalid}"),
                    encoding="utf-8",
                )
                result = run_validator(self.profile)
                output = self._output(result)

                self.assertNotEqual(0, result.returncode)
                self.assertIn(name, output)
                self.assertNotIn(invalid, output)
        env_path.write_text(original, encoding="utf-8")

    @unittest.skipIf(os.name == "nt", "POSIX permission bits are not enforced on Windows")
    def test_open_env_permissions_warn_on_posix(self) -> None:
        env_path = self.profile / ".env"
        env_path.chmod(0o644)

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertEqual(0, result.returncode, output)
        self.assertIn("WARN", output.upper())
        self.assertIn(".env", output)


if __name__ == "__main__":
    unittest.main()
