from datetime import datetime

from azure.core.exceptions import HttpResponseError
from azure.servicebus import ServiceBusMessage
from azure.servicebus.exceptions import MessageSizeExceededError, ServiceBusError

from servicebus_mcp.client import get_client


def send_batch(
    namespace: str,
    queue: str,
    messages: list[dict],
) -> str:
    service_bus_messages = []
    for m in messages:
        scheduled_time = None
        if raw_time := m.get("scheduled_enqueue_time"):
            try:
                scheduled_time = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            except ValueError:
                return f"Invalid scheduled_enqueue_time format in message: '{raw_time}'. Use ISO 8601, e.g. '2026-03-05T10:00:00Z'."
        service_bus_messages.append(ServiceBusMessage(
            m["body"],
            session_id=m.get("session_id"),
            correlation_id=m.get("correlation_id"),
            application_properties=m.get("application_properties") or {},
            scheduled_enqueue_time_utc=scheduled_time,
        ))

    try:
        client = get_client(namespace)
        with client.get_queue_sender(queue) as sender:
            batch = sender.create_message_batch()
            for msg in service_bus_messages:
                batch.add_message(msg)
            sender.send_messages(batch)
    except MessageSizeExceededError:
        return f"One or more messages exceed the size limit for queue '{queue}'."
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    return f"Batch sent successfully. {len(messages)} messages delivered to '{queue}'."
