import os
import subprocess

from azure.identity import DefaultAzureCredential
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.servicebus import ServiceBusClient
from azure.servicebus.management import ServiceBusAdministrationClient

_credential = DefaultAzureCredential()
_clients: dict[str, ServiceBusClient] = {}
_admin_clients: dict[str, ServiceBusAdministrationClient] = {}
_mgmt_client: ServiceBusManagementClient | None = None
_subscription_id: str | None = None


def get_subscription_id() -> str:
    global _subscription_id
    if _subscription_id:
        return _subscription_id

    from_env = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if from_env:
        _subscription_id = from_env
        return _subscription_id

    try:
        result = subprocess.run(
            ["az", "account", "show", "--query", "id", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            _subscription_id = result.stdout.strip()
            return _subscription_id
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    raise RuntimeError(
        "Could not determine Azure subscription ID. "
        "Set AZURE_SUBSCRIPTION_ID or run 'az login'."
    )


def get_client(namespace: str) -> ServiceBusClient:
    if not namespace.endswith(".servicebus.windows.net"):
        namespace = f"{namespace}.servicebus.windows.net"

    if namespace not in _clients:
        _clients[namespace] = ServiceBusClient(
            fully_qualified_namespace=namespace,
            credential=_credential,
        )

    return _clients[namespace]


def get_mgmt_client() -> ServiceBusManagementClient:
    global _mgmt_client
    if _mgmt_client is None:
        _mgmt_client = ServiceBusManagementClient(
            credential=_credential,
            subscription_id=get_subscription_id(),
        )
    return _mgmt_client


def get_admin_client(namespace: str) -> ServiceBusAdministrationClient:
    if not namespace.endswith(".servicebus.windows.net"):
        namespace = f"{namespace}.servicebus.windows.net"

    if namespace not in _admin_clients:
        _admin_clients[namespace] = ServiceBusAdministrationClient(
            fully_qualified_namespace=namespace,
            credential=_credential,
        )

    return _admin_clients[namespace]
