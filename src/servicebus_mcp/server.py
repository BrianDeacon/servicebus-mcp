from mcp.server.fastmcp import FastMCP

from servicebus_mcp.tools.list_queues import list_queues
from servicebus_mcp.tools.list_topics import list_topics
from servicebus_mcp.tools.peek_messages import peek_messages
from servicebus_mcp.tools.peek_subscription_messages import peek_subscription_messages
from servicebus_mcp.tools.purge_queue import purge_queue
from servicebus_mcp.tools.purge_subscription import purge_subscription
from servicebus_mcp.tools.send_batch import send_batch
from servicebus_mcp.tools.send_message import send_message

app = FastMCP("servicebus-mcp")


@app.tool()
def servicebus_list_queues(namespace: str) -> str:
    """List all queues in an Azure Service Bus namespace.

    Returns a sorted JSON array of queue names.
    The namespace can be given as a short name (e.g. shdapps-dev1-eus2-sbn)
    or as a fully qualified hostname — the .servicebus.windows.net suffix will
    be appended automatically if missing.
    """
    return list_queues(namespace)


@app.tool()
def servicebus_list_topics(namespace: str, include_subscriptions: bool = False) -> str:
    """List all topics in an Azure Service Bus namespace.

    Returns a sorted JSON array of topic names. If include_subscriptions is true,
    returns a JSON object mapping each topic name to a sorted array of its subscription names.
    The namespace can be given as a short name (e.g. shdapps-dev1-eus2-sbn)
    or as a fully qualified hostname — the .servicebus.windows.net suffix will
    be appended automatically if missing.
    """
    return list_topics(namespace, include_subscriptions)


@app.tool()
def servicebus_send_message(
    namespace: str,
    queue: str,
    body: str,
    session_id: str | None = None,
    correlation_id: str | None = None,
    application_properties: dict[str, str] | None = None,
) -> str:
    """Send a single message to an Azure Service Bus queue or topic.

    The namespace can be given as a short name (e.g. shdapps-dev1-eus2-sbn)
    or as a fully qualified hostname — the .servicebus.windows.net suffix will
    be appended automatically if missing.

    Auth uses DefaultAzureCredential. Ensure you have run 'az login' before use.
    """
    return send_message(namespace, queue, body, session_id, correlation_id, application_properties)


@app.tool()
def servicebus_send_batch(
    namespace: str,
    queue: str,
    messages: list[dict],
) -> str:
    """Send multiple messages to an Azure Service Bus queue or topic in a single batch.

    Each message in the 'messages' array should have:
      - body (string, required): the message content
      - session_id (string, optional)
      - correlation_id (string, optional)
      - application_properties (object, optional): key/value map of custom properties

    The entire batch is delivered atomically. Useful for seeding test data.
    """
    return send_batch(namespace, queue, messages)


@app.tool()
def servicebus_peek_messages(
    namespace: str,
    queue: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus queue.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies and metadata (sequence number, enqueue time, properties).
    max_count is capped at 100. For session-enabled queues, provide a session_id.
    Use servicebus_peek_messages_to_file instead if message bodies may be large.
    """
    return peek_messages(namespace, queue, max_count, session_id)


@app.tool()
def servicebus_peek_messages_to_file(
    namespace: str,
    queue: str,
    output_file: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus queue, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (sequence number, enqueue time, properties) is returned in context —
    use this variant when message bodies may be large to avoid filling the context window.
    """
    return peek_messages(namespace, queue, max_count, session_id, save_bodies_to=output_file)


@app.tool()
def servicebus_purge_queue(
    namespace: str,
    queue: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from an Azure Service Bus queue.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Will refuse to purge if the message count exceeds max_messages (default 1000)
    as a safety cap against accidentally purging queues with large backlogs.
    A warning is appended to the response for production namespaces (dco1).
    """
    return purge_queue(namespace, queue, max_messages)


@app.tool()
def servicebus_peek_subscription_messages(
    namespace: str,
    topic: str,
    subscription: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus topic subscription.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies and metadata (sequence number, enqueue time, properties).
    max_count is capped at 100.
    Use servicebus_peek_subscription_messages_to_file instead if message bodies may be large.
    """
    return peek_subscription_messages(namespace, topic, subscription, max_count)


@app.tool()
def servicebus_peek_subscription_messages_to_file(
    namespace: str,
    topic: str,
    subscription: str,
    output_file: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus topic subscription, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (sequence number, enqueue time, properties) is returned in context —
    use this variant when message bodies may be large to avoid filling the context window.
    """
    return peek_subscription_messages(namespace, topic, subscription, max_count, save_bodies_to=output_file)


@app.tool()
def servicebus_purge_subscription(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from an Azure Service Bus topic subscription.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Will refuse to purge if the message count exceeds max_messages (default 1000)
    as a safety cap against accidentally purging subscriptions with large backlogs.
    A warning is appended to the response for production namespaces (dco1).
    """
    return purge_subscription(namespace, topic, subscription, max_messages)


def main():
    app.run()


if __name__ == "__main__":
    main()
