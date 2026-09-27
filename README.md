# mem0-local-mcp

[![CI](https://github.com/ShmuelOps/mem0-local-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/ShmuelOps/mem0-local-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Long-term, semantic memory for [Claude Code](https://docs.claude.com/en/docs/claude-code) (or any
MCP client), powered by [mem0](https://github.com/mem0ai/mem0), and running **entirely on your
machine**.

- **No API key.** No OpenAI, no mem0 cloud account.
- **No local LLM needed.** Your agent (e.g. Claude) decides what's worth remembering. mem0 handles
  storage, embeddings, and semantic search.
- **Light.** Embeddings run through [FastEmbed](https://github.com/qdrant/fastembed) (ONNX, no
  PyTorch). The default model is ~67 MB and is downloaded once.
- **Private.** Memories are stored in a local [Chroma](https://www.trychroma.com/) DB. mem0
  telemetry is disabled.

## How it works

```
Claude Code ──MCP (stdio)──▶ mem0-local-mcp ──▶ mem0 ──▶ FastEmbed (local embeddings)
                                                     └─▶ Chroma (~/.mem0-local-mcp)
```

The server exposes three tools:

| Tool | What it does |
|------|--------------|
| `add_memory(text)` | Stores one fact verbatim and returns its id |
| `search_memory(query, limit=5)` | Runs a semantic search and returns `id: memory` lines |
| `delete_memory(memory_id)` | Removes a stale or wrong memory |

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.10+ (uv can install it for you)

## Install in Claude Code

```bash
claude mcp add mem0 -s user -- \
  uvx --from git+https://github.com/ShmuelOps/mem0-local-mcp mem0-local-mcp
```

`-s user` makes the memory available in every project. Use `-s project` to share the config through
`.mcp.json`, or `-s local` for the current project only.

Verify:

```bash
claude mcp list        # mem0: ... ✔ Connected
```

The first start downloads the dependencies and the embedding model, so it can take a minute.
Later starts take a few seconds.

### Tell Claude when to use it

Add this to `~/.claude/CLAUDE.md` (global) or to a project's `CLAUDE.md`:

```markdown
## Long-term memory (mem0 MCP)
- At the start of a non-trivial task, call `search_memory` with the task topic.
- When you learn a durable fact (user preference, project decision, gotcha), `search_memory`
  first, then `add_memory` one concise sentence if it's new.
- `delete_memory` entries that turn out wrong or stale.
```

### Other MCP clients

Any client that speaks MCP over stdio works. For example, Claude Desktop's
`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/ShmuelOps/mem0-local-mcp", "mem0-local-mcp"]
    }
  }
}
```

## Configuration

All configuration is optional and set through environment variables. With `claude mcp add`, pass
them as `-e KEY=value`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `MEM0_USER` | `default` | Memory namespace. Use different values to keep separate memory sets |
| `MEM0_DATA_DIR` | `~/.mem0-local-mcp` | Where the Chroma DB and history are stored |
| `MEM0_EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | Any [FastEmbed-supported model](https://qdrant.github.io/fastembed/examples/Supported_Models/) |

Example with a per-project namespace:

```bash
claude mcp add mem0 -s project -e MEM0_USER=my-project -- \
  uvx --from git+https://github.com/ShmuelOps/mem0-local-mcp mem0-local-mcp
```

> Changing `MEM0_EMBED_MODEL` after you've stored memories requires a fresh `MEM0_DATA_DIR`,
> because vectors from different models are not compatible.

## Data & privacy

- Everything is stored in `MEM0_DATA_DIR`. Delete that directory to wipe all memories.
- The only network access is the one-time download of packages and the embedding model.
- mem0 telemetry is turned off (`MEM0_TELEMETRY=False`).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `claude mcp list` shows a timeout on first run | The first launch is still downloading. Run the `uvx ...` command once in a terminal, then retry |
| Duplicate memories | This happens because `infer=False` skips mem0's LLM dedup. Keep the "search first" instruction in `CLAUDE.md` |
| Want to wipe everything | `rm -rf ~/.mem0-local-mcp` |

## Development

```bash
git clone https://github.com/ShmuelOps/mem0-local-mcp && cd mem0-local-mcp
uv sync
uv run pytest          # real end-to-end tests: mem0 + Chroma + FastEmbed, no mocks
uv run ruff check . && uv run ruff format --check .
```

Run the server from source:

```bash
claude mcp add mem0-dev -- uv run --directory "$PWD" mem0-local-mcp
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
