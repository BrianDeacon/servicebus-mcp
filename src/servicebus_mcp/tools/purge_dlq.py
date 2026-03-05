from azure.core.exceptions import HttpResponseError
from azure.servicebus import ServiceBusSubQueue
from azure.servicebus.exceptions import ServiceBusError

from servicebus_mcp.client import get_client


def purge_dlq(
    namespace: str,
    queue: str,
    max_messages: int = 1000,
) -> str:
    try:
        client = get_client(namespace)
        with client.get_queue_receiver(queue, sub_queue=ServiceBusSubQueue.DEAD_LETTER) as receiver:
            peeked = receiver.peek_messages(max_message_count=1)
            if not peeked:
                return f"Dead letter queue for '{queue}' is already empty."

            count = 0
            while True:
                messages = receiver.receive_messages(max_message_count=100, max_wait_time=5)
                if not messages:
                    break
                if count + len(messages) > max_messages:
                    receiver.close()
                    return (
                        f"Refusing to purge: dead letter queue for '{queue}' contains more than {max_messages} messages. "
                        f"Increase max_messages if you are sure."
                    )
                for msg in messages:
                    receiver.complete_message(msg)
                count += len(messages)
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    return f"Purged {count} messages from dead letter queue for '{queue}'."
