import json
from pathlib import Path

from azure.core.exceptions import HttpResponseError
from azure.servicebus import ServiceBusSubQueue
from azure.servicebus.exceptions import ServiceBusError

from servicebus_mcp.client import get_client
from servicebus_mcp.tools.utils import decode_body, decode_properties


def peek_dlq(
    namespace: str,
    queue: str,
    max_count: int = 10,
    save_bodies_to: str | None = None,
) -> str:
    if max_count > 100:
        max_count = 100

    try:
        client = get_client(namespace)
        with client.get_queue_receiver(queue, sub_queue=ServiceBusSubQueue.DEAD_LETTER) as receiver:
            peeked = receiver.peek_messages(max_message_count=max_count)
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    if not peeked:
        return f"No messages found in dead letter queue for '{queue}'."

    if save_bodies_to:
        bodies = [{"sequence_number": msg.sequence_number, "body": decode_body(msg)} for msg in peeked]
        Path(save_bodies_to).write_text(json.dumps(bodies, indent=2, default=str))

    results = [
        {
            "sequence_number": msg.sequence_number,
            "enqueued_at": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None,
            "dead_letter_reason": msg.dead_letter_reason,
            "dead_letter_error_description": msg.dead_letter_error_description,
            "session_id": msg.session_id,
            "correlation_id": msg.correlation_id,
            "application_properties": decode_properties(msg.application_properties),
            **({"body": decode_body(msg)} if not save_bodies_to else {}),
        }
        for msg in peeked
    ]

    suffix = f" Bodies saved to {save_bodies_to}." if save_bodies_to else ""
    return json.dumps(results, indent=2, default=str) + suffix
