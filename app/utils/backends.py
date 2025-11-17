from hf_http_client.factory import create_hf_http_client_from_config

from configuration import APPLICATION_NAME
from utils.tracing import propagator


def init_http_client():
    return create_hf_http_client_from_config(
        {
            "HTTP_CLIENT_FLAVOUR": "httpx",
            "HTTP_CONNECTION_TIMEOUT": 20,
            "HTTP_REQUEST_TIMEOUT": 20,
            "HTTP_MAX_CLIENT": 10,
        },
        APPLICATION_NAME,
        propagator=propagator,
    )
