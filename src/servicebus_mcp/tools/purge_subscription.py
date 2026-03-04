from azure.core.exceptions import HttpResponseError
from azure.servicebus.exceptions import ServiceBusError

from servicebus_mcp.client import get_client


def purge_subscription(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 1000,
) -> str:
    is_prod = "dco1" in namespace

    try:
        client = get_client(namespace)
        with client.get_subscription_receiver(topic, subscription) as receiver:
            peeked = receiver.peek_messages(max_message_count=1)
            if not peeked:
                return f"Subscription '{subscription}' on topic '{topic}' is already empty."

            count = 0
            while True:
                messages = receiver.receive_messages(max_message_count=100, max_wait_time=5)
                if not messages:
                    break
                if count + len(messages) > max_messages:
                    receiver.close()
                    return (
                        f"Refusing to purge: subscription '{subscription}' on topic '{topic}' "
                        f"contains more than {max_messages} messages. "
                        f"Increase max_messages if you are sure."
                    )
                for msg in messages:
                    receiver.complete_message(msg)
                count += len(messages)
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    warning = " WARNING: this was a production namespace." if is_prod else ""
    return f"Purged {count} messages from subscription '{subscription}' on topic '{topic}'.{warning}"
