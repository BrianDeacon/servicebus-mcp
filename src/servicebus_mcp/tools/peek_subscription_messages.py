import json
from pathlib import Path

from azure.core.exceptions import HttpResponseError
from azure.servicebus import NEXT_AVAILABLE_SESSION
from azure.servicebus.exceptions import OperationTimeoutError, ServiceBusError

from servicebus_mcp.client import get_admin_client, get_client
from servicebus_mcp.tools.utils import decode_body, decode_properties


def _do_peek(client, topic, subscription, max_count, session_id):
    if session_id is not None:
        with client.get_subscription_receiver(topic, subscription, session_id=session_id) as receiver:
            return receiver.peek_messages(max_message_count=max_count)

    try:
        with client.get_subscription_receiver(topic, subscription) as receiver:
            return receiver.peek_messages(max_message_count=max_count)
    except ServiceBusError:
        with client.get_subscription_receiver(
            topic, subscription, session_id=NEXT_AVAILABLE_SESSION, max_wait_time=10
        ) as receiver:
            return receiver.peek_messages(max_message_count=max_count)


def peek_subscription_messages(
    namespace: str,
    topic: str,
    subscription: str,
    max_count: int = 10,
    session_id: str | None = None,
    save_bodies_to: str | None = None,
) -> str:
    if max_count > 100:
        max_count = 100

    try:
        if session_id is None:
            props = get_admin_client(namespace).get_subscription_runtime_properties(topic, subscription)
            if props.active_message_count == 0:
                return f"No messages found in subscription '{subscription}' on topic '{topic}'."
        client = get_client(namespace)
        peeked = _do_peek(client, topic, subscription, max_count, session_id)
    except OperationTimeoutError:
        return f"Timed out waiting for an available session in subscription '{subscription}'."
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    if not peeked:
        return f"No messages found in subscription '{subscription}' on topic '{topic}'."

    if save_bodies_to:
        bodies = [{"sequence_number": msg.sequence_number, "body": decode_body(msg)} for msg in peeked]
        Path(save_bodies_to).write_text(json.dumps(bodies, indent=2, default=str))

    results = [
        {
            "sequence_number": msg.sequence_number,
            "enqueued_at": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None,
            "session_id": msg.session_id,
            "correlation_id": msg.correlation_id,
            "application_properties": decode_properties(msg.application_properties),
            **({"body": decode_body(msg)} if not save_bodies_to else {}),
        }
        for msg in peeked
    ]

    suffix = f" Bodies saved to {save_bodies_to}." if save_bodies_to else ""
    return json.dumps(results, indent=2, default=str) + suffix
