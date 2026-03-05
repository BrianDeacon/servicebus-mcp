from mcp.server.fastmcp import FastMCP

from servicebus_mcp.tools.list_namespaces import list_namespaces
from servicebus_mcp.tools.list_queues import list_queues
from servicebus_mcp.tools.list_topics import list_topics
from servicebus_mcp.tools.peek_dlq import peek_dlq
from servicebus_mcp.tools.peek_messages import peek_messages
from servicebus_mcp.tools.peek_subscription_dlq import peek_subscription_dlq
from servicebus_mcp.tools.peek_subscription_messages import peek_subscription_messages
from servicebus_mcp.tools.purge_dlq import purge_dlq
from servicebus_mcp.tools.purge_queue import purge_queue
from servicebus_mcp.tools.purge_subscription import purge_subscription
from servicebus_mcp.tools.purge_subscription_dlq import purge_subscription_dlq
from servicebus_mcp.tools.requeue_dlq import requeue_dlq
from servicebus_mcp.tools.requeue_subscription_dlq import requeue_subscription_dlq
from servicebus_mcp.tools.send_batch import send_batch
from servicebus_mcp.tools.send_message import send_message

app = FastMCP("servicebus-mcp")


@app.tool()
def servicebus_list_namespaces() -> str:
    """List all Azure Service Bus namespaces in the current subscription.

    The subscription is resolved automatically — first from the AZURE_SUBSCRIPTION_ID
    environment variable, then from the active 'az login' session. If neither is
    available, an error is returned with instructions.
    """
    return list_namespaces()


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
    scheduled_enqueue_time: str | None = None,
) -> str:
    """Send a single message to an Azure Service Bus queue or topic.

    The namespace can be given as a short name (e.g. shdapps-dev1-eus2-sbn)
    or as a fully qualified hostname — the .servicebus.windows.net suffix will
    be appended automatically if missing.

    scheduled_enqueue_time accepts an ISO 8601 string (e.g. '2026-03-05T10:00:00Z').
    If provided, the message will be enqueued at that time rather than immediately.

    Auth uses DefaultAzureCredential. Ensure you have run 'az login' before use.
    """
    return send_message(namespace, queue, body, session_id, correlation_id, application_properties, scheduled_enqueue_time)


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
      - scheduled_enqueue_time (string, optional): ISO 8601 time to enqueue the message

    The entire batch is delivered in a single send operation. Useful for seeding test data.
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
    max_count is capped at 100.
    For session-enabled queues, provide a session_id to peek a specific session.
    If session_id is omitted on a session-enabled queue, the next available session
    is accepted, peeked, and immediately released.
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
    For session-enabled queues, provide a session_id to peek a specific session.
    If session_id is omitted on a session-enabled queue, the next available session
    is accepted, peeked, and immediately released.
    """
    return peek_messages(namespace, queue, max_count, session_id, save_bodies_to=output_file)


@app.tool()
def servicebus_peek_dlq(
    namespace: str,
    queue: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for an Azure Service Bus queue.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies, dead letter reason, error description, and other metadata.
    max_count is capped at 100.
    Use servicebus_peek_dlq_to_file instead if message bodies may be large.
    """
    return peek_dlq(namespace, queue, max_count)


@app.tool()
def servicebus_peek_dlq_to_file(
    namespace: str,
    queue: str,
    output_file: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for an Azure Service Bus queue, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (dead letter reason, error description, sequence number, enqueue time) is returned in context.
    """
    return peek_dlq(namespace, queue, max_count, save_bodies_to=output_file)


@app.tool()
def servicebus_purge_dlq(
    namespace: str,
    queue: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from the dead letter queue for an Azure Service Bus queue.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_dlq(namespace, queue, max_messages)


@app.tool()
def servicebus_requeue_dlq(
    namespace: str,
    queue: str,
    max_messages: int = 100,
) -> str:
    """Move messages from a queue's dead letter queue back to the main queue.

    Each message is re-sent to the main queue preserving body, session_id, correlation_id,
    and application_properties, then completed (removed) from the dead letter queue.
    Stops if the running total would exceed max_messages.
    """
    return requeue_dlq(namespace, queue, max_messages)


@app.tool()
def servicebus_purge_queue(
    namespace: str,
    queue: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from an Azure Service Bus queue.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_queue(namespace, queue, max_messages)


@app.tool()
def servicebus_peek_subscription_messages(
    namespace: str,
    topic: str,
    subscription: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus topic subscription.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies and metadata (sequence number, enqueue time, properties).
    max_count is capped at 100.
    For session-enabled subscriptions, provide a session_id to peek a specific session.
    If session_id is omitted on a session-enabled subscription, the next available session
    is accepted, peeked, and immediately released.
    Use servicebus_peek_subscription_messages_to_file instead if message bodies may be large.
    """
    return peek_subscription_messages(namespace, topic, subscription, max_count, session_id)


@app.tool()
def servicebus_peek_subscription_messages_to_file(
    namespace: str,
    topic: str,
    subscription: str,
    output_file: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus topic subscription, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (sequence number, enqueue time, properties) is returned in context —
    use this variant when message bodies may be large to avoid filling the context window.
    For session-enabled subscriptions, provide a session_id to peek a specific session.
    If session_id is omitted on a session-enabled subscription, the next available session
    is accepted, peeked, and immediately released.
    """
    return peek_subscription_messages(namespace, topic, subscription, max_count, session_id, save_bodies_to=output_file)


@app.tool()
def servicebus_peek_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for a topic subscription.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies, dead letter reason, error description, and other metadata.
    max_count is capped at 100.
    Use servicebus_peek_subscription_dlq_to_file instead if message bodies may be large.
    """
    return peek_subscription_dlq(namespace, topic, subscription, max_count)


@app.tool()
def servicebus_peek_subscription_dlq_to_file(
    namespace: str,
    topic: str,
    subscription: str,
    output_file: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for a topic subscription, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (dead letter reason, error description, sequence number, enqueue time) is returned in context.
    """
    return peek_subscription_dlq(namespace, topic, subscription, max_count, save_bodies_to=output_file)


@app.tool()
def servicebus_purge_subscription(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from an Azure Service Bus topic subscription.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_subscription(namespace, topic, subscription, max_messages)


@app.tool()
def servicebus_purge_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from the dead letter queue for a topic subscription.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_subscription_dlq(namespace, topic, subscription, max_messages)


@app.tool()
def servicebus_requeue_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 100,
) -> str:
    """Move messages from a topic subscription's dead letter queue back to the topic.

    Each message is re-sent to the topic preserving body, session_id, correlation_id,
    and application_properties, then completed (removed) from the dead letter queue.
    Stops if the running total would exceed max_messages.
    """
    return requeue_subscription_dlq(namespace, topic, subscription, max_messages)


def main():
    app.run()


if __name__ == "__main__":
    main()
