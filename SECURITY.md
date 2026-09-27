# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue. Report privately via
[GitHub Security Advisories](https://github.com/ShmuelOps/mem0-local-mcp/security/advisories/new).
You should get a response within a few days.

## Scope

This server runs locally over stdio and stores data only in `MEM0_DATA_DIR`. It makes no network
calls apart from the one-time download of packages and the embedding model. Anything stored as a
memory is kept in plaintext on disk, so don't store secrets in it.
