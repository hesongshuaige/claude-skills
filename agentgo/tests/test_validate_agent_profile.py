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
    "FEISHU_APP_ID": "cli_test_placeholder",
    "FEISHU_APP_SECRET": "test-only-feishu-secret",
    "FEISHU_DOMAIN": "feishu",
    "FEISHU_CONNECTION_MODE": "websocket",
    "FEISHU_ALLOWED_USERS": "ou_test_placeholder",
    "FEISHU_GROUP_POLICY": "allowlist",
    "FEISHU_REQUIRE_MENTION": "true",
}


def run_validator(profile: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(profile)],
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
                ["MINIMAX_M3_API_KEY=test-only-model-secret"]
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
            "FEISHU_APP_ID=cli_test_placeholder\n"
            "FEISHU_APP_SECRET=test-only-feishu-secret\n"
            "FEISHU_DOMAIN=feishu\n"
            "FEISHU_CONNECTION_MODE=websocket\n"
            "FEISHU_ALLOWED_USERS=ou_test_placeholder\n"
            "FEISHU_GROUP_POLICY=allowlist\n"
            "FEISHU_REQUIRE_MENTION=true\n",
            encoding="utf-8",
        )

        result = run_validator(self.profile)
        output = self._output(result)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("MINIMAX_M3_API_KEY", output)
        self.assertNotIn(secret, output)

    def test_missing_workspace_fails(self) -> None:
        for path in self.workspace.iterdir():
            path.unlink()
        self.workspace.rmdir()

        result = run_validator(self.profile)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("workspace", self._output(result).lower())

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
