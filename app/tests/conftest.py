import pytest
from hf_http_client import create_hf_http_client_from_config
from hf_http_client.backends import register_backends_from_config
from starlette.testclient import TestClient

from configuration import config
from main import app
from utils.tracing import propagator

create_hf_http_client_from_config(
    {
        "HTTP_CLIENT_FLAVOUR": "httpx",
        "HTTP_CONNECTION_TIMEOUT": 20,
        "HTTP_REQUEST_TIMEOUT": 20,
        "HTTP_MAX_CLIENT": 10,
    },
    "test",
    propagator=propagator,
)
register_backends_from_config(config)


@pytest.fixture
def client():
    return TestClient(app)
