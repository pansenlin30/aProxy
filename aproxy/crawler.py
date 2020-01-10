import re
import time

from acrawler import Crawler, ParselItem, Parser, Request, get_logger, Item
from aproxy.rules import COMMON_TASKS, TEST_TASKS
from aproxy.task import ProxyGen, ProxyItemForWeb, ProxyParseItem
import asyncio
import sys
import os

logger = get_logger('aproxy')


class ProxyCrawler(Crawler):

    config = {
        'DOWNLOAD_DELAY': 3,
        'MAX_REQUESTS_PER_HOST': 1,
        'MAX_REQUESTS': 12,
        'REDIS_ENABLE': True,
        'WEB_ENABLE': True,
        # 'LOG_TO_FILE': 'proxycrawler.log'
    }
    middleware_config = {
        'aproxy.handlers.ToRedisInit': 500,
        'aproxy.handlers.WebQuery': 2000,
        'acrawler.handlers.RequestPrepareBrowser': 1000,
    }

    parsers = [Parser(css_divider='table tr', item_type=ProxyParseItem),
               Parser(css_divider='li ul', item_type=ProxyParseItem), ]

    def __init__(self):
        super().__init__()
        self.validator_cls = self.config.get('VALIDATORS', {}).values()
        self.nums = len(self.validator_cls)
        self.init_keys = ['aproxy:' + vcls.__name__ + ':init'
                          for vcls in self.validator_cls]

    async def start_requests(self):
        for info in COMMON_TASKS:
            yield ProxyGen(meta=info)

    async def next_requests(self):
        await asyncio.sleep(5)
        while (await self.sdl_req.q.get_length_of_pq()) != 0:
            await asyncio.sleep(5)
        logger.info('Sending validating signal...')
        tr = self.redis.multi_exec()

        for init_key in self.init_keys:
            pq_key = init_key.replace(
                'aproxy', 'acrawler').replace(':init', ':q:pq')
            tr.delete(pq_key)
            tr.sunionstore(init_key.replace('init', 'tmp'), init_key)
        await tr.execute()
        pass

    async def web_add_task_query(self, query: dict = None):
        validator = query.pop('v', 'bili')
        count = int(query.pop('c', 1))
        downvote = query.popall('d', [])
        task = ProxyItemForWeb(
            meta={'validator': validator, 'count': count, 'downvote': downvote})
        yield task


if __name__ == "__main__":
    ProxyCrawler().run()
