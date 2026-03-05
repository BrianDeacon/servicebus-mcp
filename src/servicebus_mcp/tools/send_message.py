from datetime import datetime
from azure.core.exceptions import HttpResponseError
from azure.servicebus import ServiceBusMessage
from azure.servicebus.exceptions import MessageSizeExceededError, ServiceBusError

from servicebus_mcp.client import get_client


def send_message(
    namespace: str,
    queue: str,
    body: str,
    session_id: str | None = None,
    correlation_id: str | None = None,
    application_properties: dict[str, str] | None = None,
    scheduled_enqueue_time: str | None = None,
) -> str:
    scheduled_time = None
    if scheduled_enqueue_time:
        try:
            scheduled_time = datetime.fromisoformat(scheduled_enqueue_time.replace("Z", "+00:00"))
        except ValueError:
            return "Invalid scheduled_enqueue_time format. Use ISO 8601, e.g. '2026-03-05T10:00:00Z'."

    message = ServiceBusMessage(
        body,
        session_id=session_id,
        correlation_id=correlation_id,
        application_properties=application_properties or {},
        scheduled_enqueue_time_utc=scheduled_time,
    )

    try:
        client = get_client(namespace)
        with client.get_queue_or_topic_sender(queue) as sender:
            sender.send_messages(message)
    except MessageSizeExceededError:
        return f"Message body is too large for queue '{queue}'."
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    if scheduled_time:
        return f"Message scheduled for {scheduled_time.isoformat()}."
    return "Message sent successfully."
