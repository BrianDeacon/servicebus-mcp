from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient
from azure.servicebus.management import ServiceBusAdministrationClient

_credential = DefaultAzureCredential()
_clients: dict[str, ServiceBusClient] = {}
_admin_clients: dict[str, ServiceBusAdministrationClient] = {}


def get_client(namespace: str) -> ServiceBusClient:
    if not namespace.endswith(".servicebus.windows.net"):
        namespace = f"{namespace}.servicebus.windows.net"

    if namespace not in _clients:
        _clients[namespace] = ServiceBusClient(
            fully_qualified_namespace=namespace,
            credential=_credential,
        )

    return _clients[namespace]


def get_admin_client(namespace: str) -> ServiceBusAdministrationClient:
    if not namespace.endswith(".servicebus.windows.net"):
        namespace = f"{namespace}.servicebus.windows.net"

    if namespace not in _admin_clients:
        _admin_clients[namespace] = ServiceBusAdministrationClient(
            fully_qualified_namespace=namespace,
            credential=_credential,
        )

    return _admin_clients[namespace]
