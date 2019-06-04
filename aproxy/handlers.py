import json
import random
import time
from collections import defaultdict
from http.cookies import Morsel

import aioredis
from yarl import URL

from acrawler import (Handler, Parser, Request, SkipTaskError, get_logger,
                      register)
from acrawler.handlers import ItemToRedis

_Redis = aioredis.Redis


class AddCookie(Handler):
    family = 'ProxyGen'

    async def on_start(self):
        self.cb_table = {}

    async def handle_before(self, task):
        if 'cookie' in task.meta:
            cookie_string = task.meta['cookie']
            url = URL(task.meta['resource'][0])
            for cs in cookie_string.split('; '):
                cs = cs.strip()

                self.crawler._session.cookie_jar.update_cookies(
                    {cs.split('=')[0]: cs.split(
                        '=')[-1]}, url)


class ToRedisInit(ItemToRedis):
    family = 'ProxyItem'

    async def handle_after(self, item):
        tr = self.redis.multi_exec()
        for key in self.crawler.init_keys:
            if 'proxy' in item:
                tr.sadd(key, item['proxy'])
        await tr.execute()
        # await self.redis.sadd(self.items_key, json.dumps(item['proxy']))


class ProxyLogRedis(Handler):
    family = 'Request'
    logger = get_logger('validator')

    async def on_start(self):
        self.keys = self.crawler.keys

        # get redis connection from crawler
        self.redis: _Redis = self.crawler.redis

    async def handle_after(self, req: Request):
        if req.exceptions or not (await self.crawler.is_ok(req.response)):
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


class WebQuery(Handler):
    family = 'ProxyItemForWeb'

    async def on_start(self):
        keys = ['score', 'speed', 'last']

        validators = self.crawler.config.get('VALIDATORS', {})
        self.keys = {}
        for v, vcls in validators.items():
            name = vcls.__name__
            d = {}
            for k in keys:
                d[k] = 'aproxy:' + name + ':' + k
            self.keys[v] = d
        self.score_limit = self.crawler.config.get('SCORE_LIMIT')
        self.speed_limit = self.crawler.config.get('SPEED_LIMIT')
        self.ttl_limit = self.crawler.config.get('TTL_LIMIT')
        self.redis = self.crawler.redis

    async def handle_before(self, item):
        start_time = int(time.time()) - self.ttl_limit

        v = item.meta['validator']
        count = item.meta['count']

        for p in item.meta['downvote']:
            await self.redis.zincrby(self.keys[v]['score'], -1, p)

        tr = self.redis.multi_exec()
        tr.zrevrangebyscore(self.keys[v]['score'], min=self.score_limit)
        tr.zrevrangebyscore(self.keys[v]['last'], min=start_time)
        tr.zrangebyscore(self.keys[v]['speed'], 0,
                         1000 * self.speed_limit)
        scored_proxies, ttl_proxies, speed_proxies = await tr.execute()
        scored_proxies, ttl_proxies, speed_proxies = set(
            scored_proxies), set(ttl_proxies), set(speed_proxies)
        proxies = scored_proxies & ttl_proxies & speed_proxies
        match = 3
        if not proxies or len(proxies) < count:
            proxies = ttl_proxies & speed_proxies
            match = 2
        if not proxies or len(proxies) < count:
            proxies = ttl_proxies | scored_proxies
            match = 1
        proxies = list(map(bytes.decode, proxies))
        random.shuffle(proxies)
        item['proxies'] = proxies[:count]
        item['count'] = len(item['proxies'])
        item['match'] = match
