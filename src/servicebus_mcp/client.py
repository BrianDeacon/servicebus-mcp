from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient

_credential = DefaultAzureCredential()
_clients: dict[str, ServiceBusClient] = {}


def get_client(namespace: str) -> ServiceBusClient:
    if not namespace.endswith(".servicebus.windows.net"):
        namespace = f"{namespace}.servicebus.windows.net"

    if namespace not in _clients:
        _clients[namespace] = ServiceBusClient(
            fully_qualified_namespace=namespace,
            credential=_credential,
        )

    return _clients[namespace]
