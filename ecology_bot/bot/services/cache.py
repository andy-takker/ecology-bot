from typing import Any

import redis


class RedisCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def get(self, name: str) -> Any:
        return self.redis_client.get(name=name)

    def set(self, name: str, value: Any, time: int | None = None) -> bool:
        return self.redis_client.set(name=name, value=value, ex=time)
