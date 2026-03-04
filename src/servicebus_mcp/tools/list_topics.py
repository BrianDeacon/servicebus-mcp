import json

from azure.core.exceptions import HttpResponseError
from azure.servicebus.exceptions import ServiceBusError

from servicebus_mcp.client import get_admin_client


def list_topics(namespace: str, include_subscriptions: bool = False) -> str:
    try:
        client = get_admin_client(namespace)
        topics = sorted(t.name for t in client.list_topics())

        if not topics:
            return f"No topics found in '{namespace}'."

        if not include_subscriptions:
            return json.dumps(topics, indent=2)

        result = {}
        for topic in topics:
            result[topic] = sorted(s.name for s in client.list_subscriptions(topic))

    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    return json.dumps(result, indent=2)
