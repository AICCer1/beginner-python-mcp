from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("beginner-python-mcp")

DATA_DIR = Path.cwd() / "data"
DB_PATH = DATA_DIR / "notes.db"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def hello(name: str = "world") -> str:
    """Return a friendly greeting. Great first MCP tool for testing."""
    return f"Hello, {name}! 来自你的 Python MCP 工具。"


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def now(mode: Literal["iso", "timestamp"] = "iso") -> str | int:
    """Return the current UTC time."""
    current = datetime.now(timezone.utc)
    if mode == "timestamp":
        return int(current.timestamp())
    return current.isoformat()


@mcp.tool()
def save_note(filename: str, content: str) -> str:
    """Save a note under the local data/ directory.

    This is intentionally sandboxed to a local folder so beginners can safely
    learn how MCP tools may write files.
    """
    safe_name = Path(filename).name
    _ensure_data_dir()
    target = DATA_DIR / safe_name
    target.write_text(content, encoding="utf-8")
    return f"Saved note to {target}"


@mcp.tool()
def init_notes_db() -> str:
    """Create a local SQLite database for note storage if it does not exist."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    return f"SQLite notes database is ready at {DB_PATH}"


@mcp.tool()
def insert_note(title: str, content: str) -> str:
    """Insert one note into the local SQLite database."""
    created_at = datetime.now(timezone.utc).isoformat()
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, created_at),
        )
        conn.commit()
    return f"Inserted note: {title}"


@mcp.tool()
def list_notes(limit: int = 10) -> list[dict[str, str | int]]:
    """List recent notes from the local SQLite database."""
    safe_limit = max(1, min(limit, 100))
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, content, created_at FROM notes ORDER BY id DESC LIMIT ?",
            (safe_limit,),
        ).fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def search_notes(keyword: str, limit: int = 10) -> list[dict[str, str | int]]:
    """Search notes by keyword in title or content."""
    safe_limit = max(1, min(limit, 100))
    pattern = f"%{keyword}%"
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, title, content, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (pattern, pattern, safe_limit),
        ).fetchall()
    return [dict(row) for row in rows]


@mcp.resource("guide://intro")
def intro_resource() -> str:
    """A tiny built-in resource that explains what this MCP server is."""
    return (
        "This is a beginner Python MCP server. It exposes simple tools like "
        "hello, add, now, save_note, and SQLite note tools so an AI agent can "
        "call them locally."
    )


@mcp.prompt()
def teaching_prompt(goal: str = "understand MCP") -> str:
    """A reusable prompt template for MCP-aware clients."""
    return (
        "You are helping a beginner learn MCP. "
        f"Their current goal is: {goal}. "
        "Explain the next step clearly, in simple language, with one example."
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
