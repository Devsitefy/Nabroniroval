import logging

import redis.asyncio as redis


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis: redis.Redis | None = None

    async def connect(self):
        logging.info("Начинаю подключение к Redis")
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True,
        )
        await self.redis.ping()
        logging.info("Успешно подключен к Redis")

    async def set(self, key: str, value: str, expire: int | None = None):
        await self.redis.set(
            name=key,
            value=value,
            ex=expire,
        )

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        return await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.aclose()
