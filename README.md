# Azure Service Bus MCP Server

An MCP (Model Context Protocol) server for Azure Service Bus. Compatible with any MCP client — Claude Code, Claude Desktop, Cursor, and others.

Exposes tools for sending messages, inspecting queue and subscription contents, and purging test data. The built-in Azure MCP server that ships with Claude Code only supports read operations (queue details, message counts, etc.) and cannot send messages — this project fills that gap.

Authentication uses `DefaultAzureCredential`, which picks up an active `az login` session automatically. Alternatively, a connection string can be provided via the `AZURE_SERVICEBUS_CONNECTION_STRING` environment variable. No secrets or connection strings are ever passed as tool arguments.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) with an active `az login` session, or `AZURE_SERVICEBUS_CONNECTION_STRING` set in your environment
- Your identity must have the **Azure Service Bus Data Owner** or **Azure Service Bus Data Receiver/Sender** roles on the target namespace

## Installation

Install `uv` if you don't have it:

### macOS

```bash
brew install uv azure-cli
```

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash   # Debian/Ubuntu
```

For other Linux distributions see the [Azure CLI install docs](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux).

### Windows

```powershell
winget install --id=astral-sh.uv
winget install --id=Microsoft.AzureCLI
```

## Configuration

**Claude Code** users:

```bash
claude mcp add --scope user azure-service-bus -- uvx servicebus-mcp
```

For other MCP clients, add the following to your server configuration:

```json
{
  "mcpServers": {
    "azure-service-bus": {
      "command": "uvx",
      "args": ["servicebus-mcp"]
    }
  }
}
```

Restart your MCP client after adding the server. No environment variables are required if you are authenticated with `az login`. Optional env vars:
- `AZURE_SUBSCRIPTION_ID` — used by `servicebus_list_namespaces` if set
- `AZURE_SERVICEBUS_CONNECTION_STRING` — use instead of `az login` for data plane operations (send, peek, purge)

### Installing from source

If you prefer to run from a local clone:

```bash
git clone https://github.com/BrianDeacon/servicebus-mcp
cd servicebus-mcp
uv sync
az login
```

Then configure with the cloned path:

```json
{
  "mcpServers": {
    "azure-service-bus": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/servicebus-mcp", "servicebus-mcp"]
    }
  }
}
```

Restart your MCP client after adding the server.

## Tools

The namespace parameter accepts either a short name (`my-namespace`) or a fully qualified hostname (`my-namespace.servicebus.windows.net`). The `.servicebus.windows.net` suffix is appended automatically if absent.

### `servicebus_list_namespaces`

List all Service Bus namespaces in the current Azure subscription. The subscription is resolved automatically — first from the `AZURE_SUBSCRIPTION_ID` environment variable, then from the active `az login` session.

### `servicebus_list_queues`

List all queues in a Service Bus namespace.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |

Returns a sorted JSON array of queue names.

### `servicebus_list_topics`

List all topics in a Service Bus namespace.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `include_subscriptions` | boolean | no | If true, returns a map of topic name → sorted array of subscription names (default false) |

### `servicebus_send_message`

Send a single message to a queue or topic.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue or topic name |
| `body` | string | yes | Message body (typically JSON, sent as-is) |
| `session_id` | string | no | Required for session-enabled queues |
| `correlation_id` | string | no | Correlation ID to set on the message |
| `application_properties` | object | no | Key/value map of custom message properties |
| `scheduled_enqueue_time` | string | no | ISO 8601 datetime to enqueue the message (e.g. `2026-03-05T10:00:00Z`). If omitted, the message is sent immediately. |

Returns a success message confirming the message was sent or scheduled.

### `servicebus_send_batch`

Send multiple messages in a single batch. Useful for seeding test data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue or topic name |
| `messages` | array | yes | Array of message objects, each with `body` (required), `session_id`, `correlation_id`, `application_properties`, and `scheduled_enqueue_time` (all optional) |

### `servicebus_peek_messages`

Non-destructively peek at messages in a queue. Messages are not locked or consumed.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |
| `session_id` | string | no | Peek within a specific session. If omitted on a session-enabled queue, the next available session is accepted, peeked, and immediately released. The session ID is included in each returned message, so you can use it for subsequent targeted calls. |

Returns message bodies and metadata (sequence number, enqueue time, properties). Use `servicebus_peek_messages_to_file` instead if message bodies may be large.

### `servicebus_peek_messages_to_file`

Same as `servicebus_peek_messages` but writes message bodies to a file. Only metadata is returned in context, avoiding large payloads filling the context window.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `output_file` | string | yes | Path to write message bodies as JSON |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |
| `session_id` | string | no | Peek within a specific session. If omitted on a session-enabled queue, the next available session is accepted, peeked, and immediately released. |

### `servicebus_peek_dlq`

Non-destructively peek at messages in a queue's dead letter queue.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |

Returns message bodies, dead letter reason, error description, and other metadata.

### `servicebus_peek_dlq_to_file`

Same as `servicebus_peek_dlq` but writes message bodies to a file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `output_file` | string | yes | Path to write message bodies as JSON |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |

### `servicebus_purge_queue`

Delete all messages from a queue. This is destructive and cannot be undone.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_messages` | integer | no | Safety cap — stops and leaves remaining messages untouched if the running total exceeds this (default 1000) |

### `servicebus_purge_dlq`

Delete all messages from a queue's dead letter queue. This is destructive and cannot be undone.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_messages` | integer | no | Safety cap — stops and leaves remaining messages untouched if the running total exceeds this (default 1000) |

### `servicebus_requeue_dlq`

Move messages from a queue's dead letter queue back to the main queue. Preserves body, session ID, correlation ID, and application properties.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_messages` | integer | no | Stops if the running total would exceed this (default 100) |

### `servicebus_peek_subscription_messages`

Non-destructively peek at messages in a topic subscription.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |
| `session_id` | string | no | Peek within a specific session. If omitted on a session-enabled subscription, the next available session is accepted, peeked, and immediately released. |

### `servicebus_peek_subscription_messages_to_file`

Same as `servicebus_peek_subscription_messages` but writes message bodies to a file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `output_file` | string | yes | Path to write message bodies as JSON |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |
| `session_id` | string | no | Peek within a specific session. If omitted on a session-enabled subscription, the next available session is accepted, peeked, and immediately released. |

### `servicebus_peek_subscription_dlq`

Non-destructively peek at messages in a topic subscription's dead letter queue.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |

### `servicebus_peek_subscription_dlq_to_file`

Same as `servicebus_peek_subscription_dlq` but writes message bodies to a file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `output_file` | string | yes | Path to write message bodies as JSON |
| `max_count` | integer | no | Max messages to return (default 10, max 100) |

### `servicebus_purge_subscription`

Delete all messages from a topic subscription. This is destructive and cannot be undone.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_messages` | integer | no | Safety cap — stops and leaves remaining messages untouched if the running total exceeds this (default 1000) |

### `servicebus_purge_subscription_dlq`

Delete all messages from a topic subscription's dead letter queue. This is destructive and cannot be undone.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_messages` | integer | no | Safety cap — stops and leaves remaining messages untouched if the running total exceeds this (default 1000) |

### `servicebus_requeue_subscription_dlq`

Move messages from a topic subscription's dead letter queue back to the topic. Preserves body, session ID, correlation ID, and application properties.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_messages` | integer | no | Stops if the running total would exceed this (default 100) |

## Security

- This server only accepts `DefaultAzureCredential` — connection strings and SAS keys are never passed as arguments, ensuring secrets do not appear in conversation history.
- `purge_*` and `requeue_*` tools enforce a `max_messages` safety cap to prevent accidental bulk operations on large backlogs.
