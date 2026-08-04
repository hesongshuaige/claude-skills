import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE_ROOT / "scripts" / "validate_feishu_url.py"

HOSTS = {
    ("feishu", "qr_url"): "accounts.feishu.cn",
    ("feishu", "verification_url"): "accounts.feishu.cn",
    ("feishu", "verification_uri_complete"): "accounts.feishu.cn",
    ("feishu", "console_url"): "open.feishu.cn",
    ("lark", "qr_url"): "accounts.larksuite.com",
    ("lark", "verification_url"): "accounts.larksuite.com",
    ("lark", "verification_uri_complete"): "accounts.larksuite.com",
    ("lark", "console_url"): "open.larksuite.com",
}


def run_validator(
    *,
    brand: str = "feishu",
    field: str = "qr_url",
    url: str = "",
    source: str = "url",
    url_file: Path | None = None,
    input_data: str | bytes | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--brand",
        brand,
        "--field",
        field,
    ]
    if source == "url":
        command.extend(("--url", url))
    elif source == "stdin":
        command.append("--stdin")
    elif source == "file":
        assert url_file is not None
        command.extend(("--url-file", str(url_file)))
    else:
        raise AssertionError(f"unknown source: {source}")

    return subprocess.run(
        command,
        text=not isinstance(input_data, (bytes, bytearray)),
        capture_output=True,
        check=False,
        timeout=10,
        input=input_data,
        cwd=cwd,
    )


class ValidateFeishuUrlTests(unittest.TestCase):
    @staticmethod
    def output(result: subprocess.CompletedProcess[str]) -> str:
        return f"{result.stdout}\n{result.stderr}"

    def test_each_brand_and_field_accepts_only_its_verified_host(self) -> None:
        for (brand, field), host in HOSTS.items():
            with self.subTest(brand=brand, field=field):
                url = f"https://{host}/device/confirm?code=opaque-value"
                result = run_validator(brand=brand, field=field, url=url)
                output = self.output(result)
                self.assertEqual(0, result.returncode, output)
                self.assertIn(f"field={field}", output)
                self.assertIn(f"brand={brand}", output)
                self.assertIn(f"host={host}", output)
                self.assertNotIn("/device/confirm", output)
                self.assertNotIn("opaque-value", output)

    def test_uppercase_hostname_is_normalized_and_accepted(self) -> None:
        result = run_validator(url="https://ACCOUNTS.FEISHU.CN/path?code=secret")

        self.assertEqual(0, result.returncode, self.output(result))
        self.assertIn("host=accounts.feishu.cn", result.stdout)
        self.assertNotIn("secret", self.output(result))

    def test_rejects_non_https_scheme(self) -> None:
        result = run_validator(url="http://accounts.feishu.cn/path?code=sensitive-http")

        self.assertEqual(1, result.returncode)
        self.assertIn("https", self.output(result).lower())
        self.assertNotIn("sensitive-http", self.output(result))

    def test_rejects_evil_suffix(self) -> None:
        result = run_validator(url="https://accounts.feishu.cn.evil.example/path")

        self.assertEqual(1, result.returncode)
        self.assertIn("host=accounts.feishu.cn.evil.example", self.output(result))

    def test_rejects_userinfo(self) -> None:
        result = run_validator(
            url="https://user:password@accounts.feishu.cn/path?code=sensitive-userinfo"
        )

        output = self.output(result)
        self.assertEqual(1, result.returncode)
        self.assertIn("userinfo", output.lower())
        self.assertNotIn("user:password", output)
        self.assertNotIn("sensitive-userinfo", output)

    def test_rejects_non_default_port(self) -> None:
        result = run_validator(url="https://accounts.feishu.cn:444/path")

        self.assertEqual(1, result.returncode)
        self.assertIn("port", self.output(result).lower())

    def test_accepts_explicit_443_port(self) -> None:
        result = run_validator(url="https://accounts.feishu.cn:443/path")

        self.assertEqual(0, result.returncode, self.output(result))

    def test_rejects_leading_or_trailing_whitespace(self) -> None:
        cases = (
            " https://accounts.feishu.cn/path?code=leading-secret",
            "https://accounts.feishu.cn/path?code=trailing-secret ",
        )
        for url in cases:
            with self.subTest(url=repr(url)):
                result = run_validator(url=url)
                output = self.output(result)
                self.assertEqual(1, result.returncode, output)
                self.assertIn("whitespace", output.lower())
                self.assertNotIn("secret", output)

    def test_rejects_ascii_controls_and_unencoded_whitespace_anywhere(self) -> None:
        cases = (
            "https://accounts.feishu.cn/path\n?code=newline-secret",
            "https://accounts.feishu.cn/pa\tth?code=tab-secret",
            "https://accounts.feishu.cn/path\x01more?code=control-secret",
            "https://accounts.feishu.cn/path with space?code=space-secret",
        )
        for url in cases:
            with self.subTest(url=repr(url)):
                result = run_validator(url=url)
                output = self.output(result)
                self.assertEqual(1, result.returncode, output)
                self.assertNotIn("secret", output)

    def test_rejects_backslash_anywhere(self) -> None:
        result = run_validator(
            url="https://accounts.feishu.cn/path\\segment?code=backslash-secret"
        )

        output = self.output(result)
        self.assertEqual(1, result.returncode, output)
        self.assertIn("backslash", output.lower())
        self.assertNotIn("backslash-secret", output)

    def test_rejects_empty_or_noncanonical_explicit_port_text(self) -> None:
        cases = (
            "https://accounts.feishu.cn:/path?code=empty-port-secret",
            "https://accounts.feishu.cn:0443/path?code=padded-port-secret",
            "https://accounts.feishu.cn:+443/path?code=signed-port-secret",
        )
        for url in cases:
            with self.subTest(url=url):
                result = run_validator(url=url)
                output = self.output(result)
                self.assertEqual(1, result.returncode, output)
                self.assertIn("port", output.lower())
                self.assertNotIn("secret", output)

    def test_rejects_percent_encoded_hostname_confusable(self) -> None:
        result = run_validator(url="https://accounts.feishu%2ecn/path")

        self.assertEqual(1, result.returncode, self.output(result))
        self.assertIn("host", self.output(result).lower())

    def test_rejects_trailing_dot_hostname(self) -> None:
        result = run_validator(url="https://accounts.feishu.cn./path")

        self.assertEqual(1, result.returncode)
        self.assertIn("host", self.output(result).lower())

    def test_rejects_unicode_hostname_confusable(self) -> None:
        result = run_validator(url="https://accounts.feishu.cп/path")

        self.assertEqual(1, result.returncode)
        self.assertIn("host", self.output(result).lower())

    def test_rejects_brand_cross_use(self) -> None:
        cases = (
            ("feishu", "qr_url", "accounts.larksuite.com"),
            ("lark", "qr_url", "accounts.feishu.cn"),
            ("feishu", "console_url", "open.larksuite.com"),
            ("lark", "console_url", "open.feishu.cn"),
        )
        for brand, field, host in cases:
            with self.subTest(brand=brand, field=field):
                result = run_validator(
                    brand=brand, field=field, url=f"https://{host}/path"
                )
                self.assertEqual(1, result.returncode)

    def test_rejects_empty_and_malformed_urls_without_traceback(self) -> None:
        cases = ("", "not a url", "https://", "https://accounts.feishu.cn:bad/path")
        for url in cases:
            with self.subTest(url=url):
                result = run_validator(url=url)
                output = self.output(result)
                self.assertEqual(1, result.returncode, output)
                self.assertNotIn("Traceback", output)

    def test_rejection_never_leaks_path_or_sensitive_query(self) -> None:
        result = run_validator(
            url="https://evil.example/private/path?token=do-not-print&code=also-secret"
        )

        output = self.output(result)
        self.assertEqual(1, result.returncode)
        self.assertNotIn("/private/path", output)
        self.assertNotIn("do-not-print", output)
        self.assertNotIn("also-secret", output)
        self.assertNotIn("token", output.lower())

    def test_cli_argument_errors_return_two_without_url_data(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--brand",
                "feishu",
                "--field",
                "qr_url",
                "--url",
                "https://evil.example/path?token=argument-secret",
                "unexpected-sensitive-argument",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )

        output = self.output(result)
        self.assertEqual(2, result.returncode, output)
        self.assertIn("reason=", output)
        self.assertNotIn("argument-secret", output)
        self.assertNotIn("unexpected-sensitive-argument", output)

    def test_help_marks_url_as_trusted_and_documents_safe_sources(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )

        self.assertEqual(0, result.returncode, self.output(result))
        self.assertIn("trusted", result.stdout.lower())
        self.assertIn("--stdin", result.stdout)
        self.assertIn("--url-file", result.stdout)

    def test_stdin_accepts_shell_metacharacters_as_data_without_creating_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            marker = "stdin-marker"
            url = (
                "https://accounts.feishu.cn/path?code=$(touch${IFS}"
                f"{marker})`touch${{IFS}}{marker}-backtick`;"
            )
            result = run_validator(
                source="stdin", input_data=url, cwd=temporary_path
            )

            self.assertEqual(0, result.returncode, self.output(result))
            self.assertFalse((temporary_path / marker).exists())
            self.assertFalse((temporary_path / f"{marker}-backtick").exists())
            self.assertNotIn("code=", self.output(result))

    def test_url_file_accepts_shell_metacharacters_as_data_without_creating_marker(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            marker = "file-marker"
            url = (
                "https://accounts.feishu.cn/path?code=$(touch${IFS}"
                f"{marker})`touch${{IFS}}{marker}-backtick`;"
            )
            url_file = temporary_path / "authorization-url.txt"
            url_file.write_bytes(url.encode("utf-8"))
            result = run_validator(
                source="file", url_file=url_file, cwd=temporary_path
            )

            self.assertEqual(0, result.returncode, self.output(result))
            self.assertFalse((temporary_path / marker).exists())
            self.assertFalse((temporary_path / f"{marker}-backtick").exists())
            self.assertNotIn("code=", self.output(result))

    def test_stdin_and_file_reject_extra_newlines_without_echoing_input(self) -> None:
        url = "https://accounts.feishu.cn/path?code=newline-secret"
        with tempfile.TemporaryDirectory() as temporary_directory:
            url_file = Path(temporary_directory) / "authorization-url.txt"
            url_file.write_bytes((url + "\n").encode("utf-8"))
            for source, input_data in (("stdin", url + "\n"), ("file", None)):
                with self.subTest(source=source):
                    result = run_validator(
                        source=source,
                        url_file=url_file,
                        input_data=input_data,
                    )
                    output = self.output(result)
                    self.assertEqual(1, result.returncode, output)
                    self.assertNotIn("newline-secret", output)

    def test_rejects_bad_utf8_from_stdin_and_file_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            url_file = Path(temporary_directory) / "bad-url.txt"
            url_file.write_bytes(b"https://accounts.feishu.cn/path?code=\xff")
            for source, input_data in (("stdin", b"\xff"), ("file", None)):
                with self.subTest(source=source):
                    result = run_validator(
                        source=source,
                        url_file=url_file,
                        input_data=input_data,
                    )
                    output = self.output(result)
                    self.assertEqual(1, result.returncode, output)
                    self.assertNotIn("Traceback", output)
                    self.assertNotIn("code=", output)

    def test_rejects_missing_url_file_without_echoing_path(self) -> None:
        missing_file = Path(tempfile.gettempdir()) / "missing-authorization-url.txt"
        if missing_file.exists():
            missing_file.unlink()
        result = run_validator(source="file", url_file=missing_file)

        output = self.output(result)
        self.assertEqual(1, result.returncode, output)
        self.assertNotIn(str(missing_file), output)
        self.assertNotIn("Traceback", output)

    def test_input_sources_are_mutually_exclusive_and_required(self) -> None:
        common = [
            sys.executable,
            str(SCRIPT),
            "--brand",
            "feishu",
            "--field",
            "qr_url",
        ]
        cases = (
            common + ["--stdin", "--url", "https://accounts.feishu.cn/path"],
            common + ["--stdin", "--url-file", "url.txt"],
            common,
        )
        for command in cases:
            with self.subTest(command=command):
                result = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                output = self.output(result)
                self.assertEqual(2, result.returncode, output)
                self.assertNotIn("accounts.feishu.cn", output)
                self.assertNotIn("url.txt", output)

    def test_rejects_input_larger_than_64_kib(self) -> None:
        oversized_url = (
            "https://accounts.feishu.cn/path?code=" + "a" * (64 * 1024)
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            url_file = Path(temporary_directory) / "oversized-url.txt"
            url_file.write_bytes(oversized_url.encode("ascii"))
            for source, input_data in (("stdin", oversized_url), ("file", None)):
                with self.subTest(source=source):
                    result = run_validator(
                        source=source,
                        url_file=url_file,
                        input_data=input_data,
                    )
                    self.assertEqual(1, result.returncode, self.output(result))
                    self.assertNotIn("a" * 100, self.output(result))


if __name__ == "__main__":
    unittest.main()
