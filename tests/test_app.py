"""Unit tests for the Flask SQL query runner in app.py.

The database layer (pymysql.connect) is mocked out, so these tests exercise
the route logic — request handling, result passing to the template, and
error/connection-cleanup behavior — without a live MySQL server.
"""
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module  # noqa: E402

app_module.app.config["TESTING"] = True


def make_cursor(rows):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    connection = MagicMock()
    # 'with connection.cursor() as cursor:'
    connection.cursor.return_value.__enter__.return_value = cursor
    return connection, cursor


def test_home_page_renders_query_form():
    client = app_module.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Wentworth Database" in html
    assert "Enter your SQL query here" in html


def test_post_query_runs_and_renders_results():
    connection, cursor = make_cursor(
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    )
    client = app_module.app.test_client()
    with patch("app.pymysql.connect", return_value=connection):
        resp = client.post("/", data={"query": "SELECT id, name FROM students"})
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Alice" in html and "Bob" in html
    assert "<th>id</th>" in html and "<th>name</th>" in html
    cursor.execute.assert_called_once_with("SELECT id, name FROM students")


def test_post_query_passes_query_through_verbatim():
    connection, cursor = make_cursor([])
    client = app_module.app.test_client()
    with patch("app.pymysql.connect", return_value=connection):
        client.post("/", data={"query": "SHOW TABLES"})
    cursor.execute.assert_called_once_with("SHOW TABLES")


def test_db_error_is_shown_not_raised():
    client = app_module.app.test_client()
    with patch(
        "app.pymysql.connect", side_effect=Exception("connection refused")
    ):
        resp = client.post("/", data={"query": "SELECT 1"})
    assert resp.status_code == 200
    assert "connection refused" in resp.get_data(as_text=True)


def test_connection_closed_on_success():
    connection, _ = make_cursor([{"a": 1}])
    client = app_module.app.test_client()
    with patch("app.pymysql.connect", return_value=connection):
        client.post("/", data={"query": "SELECT 1"})
    connection.close.assert_called_once()


def test_connection_closed_on_error():
    connection = MagicMock()
    connection.cursor.side_effect = Exception("cursor boom")
    client = app_module.app.test_client()
    with patch("app.pymysql.connect", return_value=connection):
        resp = client.post("/", data={"query": "SELECT 1"})
    assert resp.status_code == 200
    assert "cursor boom" in resp.get_data(as_text=True)
    connection.close.assert_called_once()


def test_results_table_column_headers_come_from_row_keys():
    connection, _ = make_cursor([{"x": 10, "y": 20}])
    client = app_module.app.test_client()
    with patch("app.pymysql.connect", return_value=connection):
        resp = client.post("/", data={"query": "SELECT x, y FROM t"})
    html = resp.get_data(as_text=True)
    assert "<th>x</th>" in html and "<th>y</th>" in html
    assert "<td>10</td>" in html and "<td>20</td>" in html
