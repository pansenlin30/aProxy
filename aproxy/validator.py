import asyncio
import json
import time

from acrawler import Crawler, Handler, Item, Request, Response, get_logger
from aproxy.handlers import RequestSpeed
import aioredis
import random


logger = get_logger('validator')


class ValidatedItem(Item):

    def __init__(self, name, extra=None, **kwargs):
        super().__init__(**kwargs)
        self.content['name'] = name
        self.content['speed'] = None
        self.content['last'] = None
        self.content['score'] = 5
        self.content.update(extra)


class HTTPValidator(Crawler):
    middleware_config = {
        'aproxy.handlers.RequestSpeed': 1000,
        'aproxy.handlers.ProxyLogRedis': 800
    }
    config = {
        'REDIS_ENABLE': True,
    }

    url = 'http://httpbin.org/headers?show_env'

    def __init__(self):
        super().__init__()
        self.config['MAX_REQUESTS'] = self.config.get(
            'MAX_REQUESTS_FOR_VALIDATOR', 20)
        self.origin_ip = ''
        self.name = self.__class__.__name__
        key_names = ['init', 'tmp', 'last', 'speed', 'score']

        # get five redis keys
        self.keys = {
            k: 'aproxy:' + self.name + ':' + k for k in key_names
        }
        self.redis: aioredis.Redis

    async def next_requests(self):

        while 1:
            proxy = await self.redis.spop(self.keys['tmp'])
            if proxy:
                proxy = proxy.decode()
                old_score = await self.redis.zscore(self.keys['score'], proxy)
                req = Request(self.url,
                              # this will allow any response's status
                              status_allowed=[],
                              # this will not retry the request.
                              ignore_exception=True,
                              dont_filter=True,
                              request_config={
                                  'timeout': 40,
                                  'proxy': 'http://' + proxy},
                              meta={'proxy': proxy, 'old_score': old_score})
                await self.add_task(req)
            else:
                await asyncio.sleep(5)

    async def start_requests(self):
        pass

    async def get_origin_ip(self):
        """Make request to httpbin to get original IP."""
        r = Request('http://httpbin.org/headers?show_env')
        resp = await r.fetch()
        self.origin_ip = resp.json['headers']['X-Real-Ip']


if __name__ == "__main__":
    HTTPValidator().run()