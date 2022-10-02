import redis
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from pydantic import RedisDsn

from ecology_bot.bot.services.cache import RedisCache


class RedisMiddleware(LifetimeControllerMiddleware):
    def __init__(self, redis_uri: RedisDsn):
        super().__init__()
        self.redis = redis.StrictRedis(
            host=redis_uri.host,
            port=redis_uri.port,
            password=redis_uri.password,
            max_connections=10,
        )

    async def pre_process(self, obj, data, *args):
        data['cache'] = RedisCache(self.redis)

    async def post_process(self, obj, data, *args):
        del data['cache']
