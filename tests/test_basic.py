from commitai import __version__
from commitai.ai_client import _parse_json


def test_version():
    assert __version__ == "0.1.0"


def test_parse_json_array():
    result = _parse_json('["feat: add login", "fix: handle edge case"]')
    assert result == ["feat: add login", "fix: handle edge case"]


def test_parse_json_embedded():
    result = _parse_json('Here:\n["feat: add login", "fix: edge case"]\nDone.')
    assert result == ["feat: add login", "fix: edge case"]


def test_parse_json_fallback():
    result = _parse_json("feat: add login\nfix: handle edge case")
    assert "feat: add login" in result
