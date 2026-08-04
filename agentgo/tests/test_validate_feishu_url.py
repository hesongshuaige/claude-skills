import subprocess
import sys
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
    *, brand: str = "feishu", field: str = "qr_url", url: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--brand",
            brand,
            "--field",
            field,
            "--url",
            url,
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
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


if __name__ == "__main__":
    unittest.main()
