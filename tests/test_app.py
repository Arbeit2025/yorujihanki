import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402


def test_index_ok_and_title():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "夜の自販機" in html


def test_healthz():
    client = app.test_client()
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.get_data(as_text=True) == "ok"


def test_script_not_escaped():
    # |safe 回帰テスト: JS が HTML エスケープされて死んでいないこと
    client = app.test_client()
    html = client.get("/").get_data(as_text=True)
    assert "getElementById" in html
    assert "&#34;" not in html
    assert "&#39;" not in html
