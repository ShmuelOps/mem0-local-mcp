"""Local mem0 long-term memory as an MCP server. No API key, no cloud."""

import os
from functools import cache
from pathlib import Path

DEFAULT_DATA_DIR = "~/.mem0-local-mcp"
DEFAULT_EMBED_MODEL = "BAAI/bge-small-en-v1.5"

os.environ.setdefault("MEM0_TELEMETRY", "False")
# mem0 writes config.json to MEM0_DIR (default ~/.mem0) at import; keep it with our data.
os.environ.setdefault(
    "MEM0_DIR", str(Path(os.environ.get("MEM0_DATA_DIR", DEFAULT_DATA_DIR)).expanduser())
)

from mcp.server.fastmcp import FastMCP  # noqa: E402
from mem0 import Memory  # noqa: E402

mcp = FastMCP("mem0")


def _user() -> str:
    return os.environ.get("MEM0_USER", "default")


@cache
def memory() -> Memory:
    data_dir = Path(os.environ.get("MEM0_DATA_DIR", DEFAULT_DATA_DIR)).expanduser()
    return Memory.from_config(
        {
            # mem0 builds an LLM client eagerly even when unused. We always call
            # add(infer=False) - the calling agent decides what to remember -
            # so this client is never invoked and the key is a placeholder.
            "llm": {"provider": "openai", "config": {"api_key": "unused"}},
            "embedder": {
                "provider": "fastembed",
                "config": {"model": os.environ.get("MEM0_EMBED_MODEL", DEFAULT_EMBED_MODEL)},
            },
            "vector_store": {
                "provider": "chroma",
                "config": {"collection_name": "memories", "path": str(data_dir / "chroma")},
            },
            "history_db_path": str(data_dir / "history.db"),
        }
    )


@mcp.tool()
def add_memory(text: str) -> str:
    """Store one concise, durable fact worth remembering across sessions.

    Search first to avoid duplicates. Returns the new memory id.
    """
    return memory().add(text, user_id=_user(), infer=False)["results"][0]["id"]


@mcp.tool()
def search_memory(query: str, limit: int = 5) -> str:
    """Semantic search over long-term memory. Returns one 'id: memory' per line."""
    hits = memory().search(query, filters={"user_id": _user()}, top_k=limit)["results"]
    return "\n".join(f"{h['id']}: {h['memory']}" for h in hits) or "no memories"


@mcp.tool()
def delete_memory(memory_id: str) -> str:
    """Delete a stale or wrong memory by id."""
    memory().delete(memory_id)
    return "deleted"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
