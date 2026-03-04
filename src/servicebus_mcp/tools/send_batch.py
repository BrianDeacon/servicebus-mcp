from azure.core.exceptions import HttpResponseError
from azure.servicebus import ServiceBusMessage
from azure.servicebus.exceptions import MessageSizeExceededError, ServiceBusError

from servicebus_mcp.client import get_client


def send_batch(
    namespace: str,
    queue: str,
    messages: list[dict],
) -> str:
    service_bus_messages = [
        ServiceBusMessage(
            m["body"],
            session_id=m.get("session_id"),
            correlation_id=m.get("correlation_id"),
            application_properties=m.get("application_properties") or {},
        )
        for m in messages
    ]

    try:
        client = get_client(namespace)
        with client.get_queue_or_topic_sender(queue) as sender:
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
