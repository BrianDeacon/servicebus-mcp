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
) -> str:
    message = ServiceBusMessage(
        body,
        session_id=session_id,
        correlation_id=correlation_id,
        application_properties=application_properties or {},
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

    seq = message.sequence_number
    if seq is not None:
        return f"Message sent successfully. Sequence number: {seq}"
    return "Message sent successfully."
