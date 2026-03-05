import json

from azure.core.exceptions import HttpResponseError

from servicebus_mcp.client import get_mgmt_client


def list_namespaces() -> str:
    try:
        client = get_mgmt_client()
        namespaces = sorted(ns.name for ns in client.namespaces.list())
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except RuntimeError as e:
        return str(e)

    if not namespaces:
        return "No Service Bus namespaces found in the current subscription."

    return json.dumps(namespaces, indent=2)
