import json

from azure.core.exceptions import HttpResponseError
from azure.servicebus.exceptions import ServiceBusError

from servicebus_mcp.client import get_admin_client


def list_queues(namespace: str) -> str:
    try:
        client = get_admin_client(namespace)
        queues = [q.name for q in client.list_queues()]
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceBusError as e:
        return f"Service Bus error: {e}"

    if not queues:
        return f"No queues found in '{namespace}'."

    return json.dumps(sorted(queues), indent=2)
