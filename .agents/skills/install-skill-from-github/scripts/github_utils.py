#!/usr/bin/env python3
"""GitHub requests; adapted from OpenAI skill-installer (see ../UPSTREAM.md)."""

from __future__ import annotations

import os
import urllib.parse
import urllib.request


def github_request(url: str, user_agent: str) -> bytes:
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname
        not in {"api.github.com", "codeload.github.com", "raw.githubusercontent.com"}
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Unsupported GitHub request URL")
    headers = {"User-Agent": user_agent}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def github_api_contents_url(repo: str, path: str, ref: str) -> str:
    return f"https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(path, safe='/')}?ref={urllib.parse.quote(ref, safe='')}"


def redact_credentials(message: str) -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(key)
        if value:
            message = message.replace(value, "[REDACTED]")
    return message
