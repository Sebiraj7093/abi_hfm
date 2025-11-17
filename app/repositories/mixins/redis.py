from hf_redis_client.client import RedisSlaveClient
from hf_redis_client.master import RedisMasterClient

from configuration import config
from utils.tracing import TracerMixin


class RedisMixin(metaclass=TracerMixin):
    @property
    def redis_client(self) -> RedisSlaveClient:
        return RedisSlaveClient(config)

    @property
    def redis_master_client(self) -> RedisMasterClient:
        return RedisMasterClient(config)
