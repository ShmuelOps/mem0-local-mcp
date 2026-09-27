"""End-to-end tests: real mem0 + Chroma + FastEmbed, no mocks."""

import asyncio
import os
import subprocess
import sys

import pytest

from mem0_local_mcp import server


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MEM0_USER", "test-user")
    server.memory.cache_clear()
    yield
    server.memory.cache_clear()


def test_tools_registered():
    tools = asyncio.run(server.mcp.list_tools())
    assert {t.name for t in tools} == {"add_memory", "search_memory", "delete_memory"}


def test_empty_search():
    assert server.search_memory("anything") == "no memories"


def test_add_search_delete_roundtrip():
    mid = server.add_memory("The user prefers uv over pip for Python packaging")
    server.add_memory("The office coffee machine is on the third floor")

    first = server.search_memory("which python package manager?", limit=1)
    assert first == f"{mid}: The user prefers uv over pip for Python packaging"

    assert server.delete_memory(mid) == "deleted"
    assert mid not in server.search_memory("python package manager")


def test_memories_are_scoped_per_user(monkeypatch):
    server.add_memory("secret belonging to test-user")
    monkeypatch.setenv("MEM0_USER", "someone-else")
    assert server.search_memory("secret") == "no memories"


def test_nothing_written_to_default_mem0_home(tmp_path):
    # Fresh interpreter: mem0 decides its home dir at import time.
    env = {k: v for k, v in os.environ.items() if not k.startswith("MEM0_")}
    env["HOME"] = str(tmp_path)
    code = "from mem0_local_mcp import server; server.memory()"
    subprocess.run([sys.executable, "-c", code], env=env, check=True, capture_output=True)
    assert not (tmp_path / ".mem0").exists()
    assert (tmp_path / ".mem0-local-mcp" / "config.json").exists()
