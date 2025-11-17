from hf_http_client.backends import mongo_internal_hf_api
from hf_mongo_client.api import MongoApiClient

from utils.tracing import TracerMixin


class MongoMixin(metaclass=TracerMixin):
    @property
    def mongo_internal_api_client(self) -> MongoApiClient:
        return MongoApiClient(mongo_internal_hf_api)
