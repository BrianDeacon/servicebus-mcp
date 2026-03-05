# Contributing

Contributions are welcome. Here's how to get started.

## Setup

```bash
git clone https://github.com/BrianDeacon/servicebus-mcp
cd servicebus-mcp
uv sync
az login
```

Register the local version with your MCP client:

```bash
claude mcp add --scope user azure-service-bus -- uv run --directory /path/to/servicebus-mcp servicebus-mcp
```

## Making changes

- Tools live in `src/servicebus_mcp/tools/` — one file per tool
- Register new tools in `src/servicebus_mcp/server.py` with an `@app.tool()` decorator
- The tool's docstring is what the AI reads — make it clear and accurate
- Test manually against a real Service Bus namespace before submitting

## Submitting a PR

- Open an issue first for anything non-trivial so we can align before you build it
- Keep PRs focused — one feature or fix per PR
- Update the README if you're adding or changing a tool

## Reporting bugs

Open an issue at https://github.com/BrianDeacon/servicebus-mcp/issues with enough detail to reproduce it — which tool, what namespace (redacted if needed), and what you expected vs. what happened.
