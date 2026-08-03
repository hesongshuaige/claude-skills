import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE_ROOT / "scripts" / "validate_agent_profile.py"
CONTEXT_FILES = ("SOUL.md", "AGENTS.md", "README.md", "PROJECT.md")


def run_validator(profile: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(profile)],
        text=True,
        capture_output=True,
        check=False,
    )


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
                (
                    "MINIMAX_M3_API_KEY=test-only-model-secret",
                    "FEISHU_APP_ID=cli_test_placeholder",
                    "FEISHU_APP_SECRET=test-only-feishu-secret",
                    "FEISHU_DOMAIN=feishu",
                    "FEISHU_CONNECTION_MODE=websocket",
                    "FEISHU_ALLOWED_USERS=ou_test_placeholder",
                    "FEISHU_GROUP_POLICY=allowlist",
                    "FEISHU_REQUIRE_MENTION=true",
                    "",
                )
            ),
            encoding="utf-8",
        )
        (self.profile / "SOUL.md").write_text("# Test Agent\n", encoding="utf-8")
        for filename in CONTEXT_FILES:
            (self.workspace / filename).write_text(
                f"# {filename}\nTest context.\n", encoding="utf-8"
            )

    @staticmethod
    def _output(result: subprocess.CompletedProcess[str]) -> str:
        return f"{result.stdout}\n{result.stderr}"

    def test_complete_profile_passes(self) -> None:
        result = run_validator(self.profile)

        self.assertEqual(0, result.returncode, self._output(result))

    def test_missing_required_file_fails(self) -> None:
        (self.profile / "config.yaml").unlink()

        result = run_validator(self.profile)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("config.yaml", self._output(result))

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
        self.assertIn("everyone", output)

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
