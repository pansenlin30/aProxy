from acrawler import Handler, register, SkipTaskError, Request, get_logger
from acrawler.handlers import ItemToRedis
import json
import time
import aioredis
_Redis = aioredis.Redis


class ToRedisInit(ItemToRedis):
    family = 'ProxyItem'

    async def on_start(self):
        await super().on_start()
        self.keys = ['aproxy:' + name + ':init'
                     for name in self.crawler.config.get('VALIDATOR_NAMES', [])]

    async def handle_after(self, item):
        tr = self.redis.multi_exec()
        for key in self.keys:
            tr.sadd(key, item['proxy'])
        await tr.execute()
        # await self.redis.sadd(self.items_key, json.dumps(item['proxy']))


class ProxyLogRedis(Handler):
    family = 'Request'
    # logger = get_logger('validator')

    async def on_start(self):
        self.keys = self.crawler.keys

        # get redis connection from crawler
        self.redis: _Redis = self.crawler.redis

    async def handle_after(self, req: Request):
        if req.exceptions:
            await self.update_proxy_to_redis(req.meta['proxy'], False, old_score=req.meta['old_score'])
        else:
            await self.update_proxy_to_redis(
                req.meta['proxy'], True, req.meta['speed'], int(time.time()), req.meta['old_score'])

    async def update_proxy_to_redis(self,
                                    proxy: str,
                                    success: bool,
                                    speed: int = None,
                                    last: int = None,
                                    old_score: int = None):
        """Update infos in three redis sorted sets."""
        if success:
            tr = self.redis.multi_exec()
            tr.zadd(self.keys['speed'], speed, proxy)
            tr.zadd(self.keys['last'], last, proxy)
            if old_score is None or old_score < 5:
                tr.zincrby(self.keys['score'], 1, proxy)
            else:
                tr.zincrby(self.keys['score'], round(5 / old_score, 2), proxy)
            await tr.execute()
            # self.logger.info('{} speed:{}'.format(proxy, speed))
        else:
            if old_score and old_score <= -4:
                await self.delete_proxy(proxy)
                # self.logger.info('delete proxy:{}'.format(proxy))
            else:
                await self.redis.zincrby(self.keys['score'], -1, proxy)
                # self.logger.info('proxy failed:{}'.format(proxy))

    async def delete_proxy(self, proxy: str):
        tr = self.redis.multi_exec()
        tr.zrem(self.keys['speed'], proxy)
        tr.zrem(self.keys['last'], proxy)
        tr.zrem(self.keys['score'], proxy)
        tr.srem(self.keys['init'], proxy)
        await tr.execute()


class RequestSpeed(Handler):
    family = 'Request'

    async def handle_before(self, task):
        task.meta['start'] = int(time.time() * 1000)

    async def handle_after(self, task):
        task.meta['speed'] = int(time.time() * 1000) - task.meta['start']
