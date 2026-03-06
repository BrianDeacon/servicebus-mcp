from azure.core.exceptions import HttpResponseError
from azure.servicebus import ServiceBusMessage, ServiceBusSubQueue
from azure.servicebus.exceptions import ServiceBusError

from servicebus_mcp.client import get_client


def requeue_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 100,
) -> str:
    try:
        client = get_client(namespace)
        with client.get_subscription_receiver(topic, subscription, sub_queue=ServiceBusSubQueue.DEAD_LETTER) as receiver:
            peeked = receiver.peek_messages(max_message_count=1)
            if not peeked:
                return f"Dead letter queue for subscription '{subscription}' on topic '{topic}' is already empty."

            count = 0
            with client.get_topic_sender(topic) as sender:
                while True:
                    messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                    if not messages:
                        break
                    if count + len(messages) > max_messages:
                        return (
                            f"Stopping: would exceed max_messages ({max_messages}). "
                            f"Requeued {count} messages so far."
                        )
                    for msg in messages:
                        requeued = ServiceBusMessage(
                            body=msg.body,
                            session_id=msg.session_id,
                            correlation_id=msg.correlation_id,
                            application_properties=msg.application_properties,
                        )
                        sender.send_messages(requeued)
                        receiver.complete_message(msg)
                        count += 1
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    return f"Requeued {count} messages from dead letter queue for subscription '{subscription}' back to topic '{topic}'."
