"""Tests for janusbootctl / hello About (Golden Path UPG-78)."""

from hello.about import about_payload as hello_about_payload
from janusbootctl.about import APP_VERSION, about_payload, about_summary


def test_about_includes_version_and_donate() -> None:
    text = about_summary()
    assert APP_VERSION in text
    assert "JanusBoot" in text
    assert "donate" in text


def test_about_payload_matches_shared_contract() -> None:
    payload = about_payload()
    assert payload["version"] == APP_VERSION
    assert payload["donate"].startswith("http")
    assert payload["summary"] == about_summary()
    assert payload["update"] == {"status": "current", "version": None, "url": None}


def test_hello_about_reexports_janusbootctl() -> None:
    assert hello_about_payload() == about_payload()
