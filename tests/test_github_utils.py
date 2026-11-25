"""GitHub helpers use bounded requests and do not send tokens to arbitrary hosts."""

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/install-skill-from-github/scripts/github_utils.py"
)
spec = importlib.util.spec_from_file_location("github_helpers", SCRIPT)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def test_contents_url_encodes_query_and_unicode():
    url = helpers.github_api_contents_url(
        "owner/repo", "目录 with space/SKILL.md", "feature/a&b"
    )
    assert "feature%2Fa%26b" in url
    assert " " not in url


def test_request_uses_timeout_and_auth_without_printing():
    with (
        patch.dict(helpers.os.environ, {"GITHUB_TOKEN": "secret-value"}),
        patch.object(helpers.urllib.request, "urlopen") as open_url,
    ):
        open_url.return_value.__enter__.return_value.read.return_value = b"data"
        assert (
            helpers.github_request("https://api.github.com/repos/o/r", "test")
            == b"data"
        )
        assert open_url.call_args.kwargs["timeout"] == 30
        assert (
            open_url.call_args.args[0].get_header("Authorization")
            == "token secret-value"
        )
        assert helpers.redact_credentials("failed secret-value") == "failed [REDACTED]"


@pytest.mark.parametrize(
    "url",
    [
        "http://api.github.com/x",
        "https://evil.example/x",
        "https://user:pass@api.github.com/x",
    ],
)
def test_invalid_hosts_are_rejected_before_request(url):
    with patch.object(helpers.urllib.request, "urlopen") as request:
        with pytest.raises(ValueError):
            helpers.github_request(url, "test")
        request.assert_not_called()
