#!/usr/bin/env python3
"""Validate Feishu/Lark authorization URLs without opening or changing them."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence
from urllib.parse import urlsplit


ACCOUNT_FIELDS = (
    "qr_url",
    "verification_url",
    "verification_uri_complete",
)
FIELDS = ACCOUNT_FIELDS + ("console_url",)
HOSTS = {
    "feishu": {
        "account": "accounts.feishu.cn",
        "console_url": "open.feishu.cn",
    },
    "lark": {
        "account": "accounts.larksuite.com",
        "console_url": "open.larksuite.com",
    },
}


class SafeArgumentParser(argparse.ArgumentParser):
    """Keep parser failures from echoing URL-shaped argument data."""

    def error(self, message: str) -> None:
        del message
        self.exit(
            2,
            "[ERROR] field=<invalid> brand=<invalid> host=<unparsed> "
            "reason=invalid arguments\n",
        )


@dataclass(frozen=True)
class ValidationResult:
    accepted: bool
    host: str
    reason: str


def validate_url(brand: str, field: str, url: str) -> ValidationResult:
    """Return an offline, fail-closed validation result for an opaque URL."""
    expected_host = HOSTS[brand]["account" if field in ACCOUNT_FIELDS else field]
    if any(ord(character) < 32 or ord(character) == 127 for character in url):
        return ValidationResult(False, "<unparsed>", "ASCII control characters are forbidden")
    if any(character.isspace() for character in url):
        return ValidationResult(False, "<unparsed>", "unencoded whitespace is forbidden")
    if "\\" in url:
        return ValidationResult(False, "<unparsed>", "backslash is forbidden")

    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return ValidationResult(False, "<invalid>", "URL parsing failed")

    separator = url.find("://")
    if separator < 0:
        return ValidationResult(False, "<missing>", "URL authority is missing")
    authority_start = separator + 3
    authority_end = len(url)
    for delimiter in "/?#":
        delimiter_index = url.find(delimiter, authority_start)
        if delimiter_index >= 0:
            authority_end = min(authority_end, delimiter_index)
    authority = url[authority_start:authority_end]

    hostname = parsed.hostname
    host = hostname.lower() if hostname else "<missing>"
    if parsed.scheme.lower() != "https":
        return ValidationResult(False, host, "scheme must be https")
    if "@" in authority or parsed.username is not None or parsed.password is not None:
        return ValidationResult(False, host, "userinfo is forbidden")

    raw_host = authority
    if ":" in authority:
        raw_host, separator, raw_port = authority.rpartition(":")
        if separator and raw_port != "443":
            return ValidationResult(False, host, "explicit port text must be exactly 443")
    if not raw_host or not raw_host.isascii() or "%" in raw_host:
        return ValidationResult(False, "<invalid>", "host text is invalid")

    try:
        port = parsed.port
    except ValueError:
        return ValidationResult(False, "<invalid>", "port is invalid")
    if port not in (None, 443):
        return ValidationResult(False, host, "port must be omitted or 443")
    if hostname is None:
        return ValidationResult(False, host, "host is missing")
    if not hostname.isascii():
        return ValidationResult(False, host, "host must contain ASCII characters only")
    if hostname.endswith("."):
        return ValidationResult(False, host, "host must not have a trailing dot")
    if host != expected_host:
        return ValidationResult(False, host, "host does not match brand and field")
    return ValidationResult(True, host, "validated")


def main(argv: Sequence[str] | None = None) -> int:
    parser = SafeArgumentParser(
        description="Validate a Feishu/Lark authorization URL offline"
    )
    parser.add_argument("--brand", choices=tuple(HOSTS), required=True)
    parser.add_argument("--field", choices=FIELDS, required=True)
    parser.add_argument("--url", required=True)
    arguments = parser.parse_args(argv)

    result = validate_url(arguments.brand, arguments.field, arguments.url)
    status = "PASS" if result.accepted else "REJECT"
    print(
        f"[{status}] field={arguments.field} brand={arguments.brand} "
        f"host={result.host} reason={result.reason}"
    )
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
