import re
import time

from acrawler import Crawler, ParselItem, Parser, Request, get_logger, Item
from aproxy.rules import COMMON_TASKS
from aproxy.task import ProxyGen, ProxyItemForWeb
import asyncio
import sys
import os

logger = get_logger('aproxy')

PATTERN = re.compile(
    r'\b((?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))\D*([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])')


class ProxyItem(ParselItem):

    def custom_process(self, content):
        match = PATTERN.search(self.sel.xpath("string(.)").get())
        if match:
            ip = match.groups()[0]
            port = match.groups()[1]
            content['proxy'] = ip+':'+port
            # logger.info(content['proxy'])


class ProxyCrawler(Crawler):

    config = {
        'DOWNLOAD_DELAY': 2,
        'MAX_REQUESTS_PER_HOST': 1,
        'MAX_REQUESTS': 8,
        'REDIS_ENABLE': True,
        'WEB_ENABLE': True,
        'LOG_TO_FILE': 'proxycrawler.log'
    }
    middleware_config = {
        'aproxy.handlers.ToRedisInit': 500,
        'aproxy.handlers.WebQuery': 2000,
    }

    parsers = [Parser(css_divider='table tr', item_type=ProxyItem),
               Parser(css_divider='li ul', item_type=ProxyItem), ]

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
        interval = self.config.get('REVALIDATE_TIME', 15 * 60)
        await asyncio.sleep(5)
        while 1:
            while (await self.sdl_req.q.get_length_of_pq()) != 0:
                await asyncio.sleep(5)
            logger.info('Sending validating signal...')
            tr = self.redis.multi_exec()
            for init_key in self.init_keys:
                tr.sunionstore(init_key.replace('init', 'tmp'), init_key)
            await tr.execute()
            await asyncio.sleep(interval)

    async def web_add_task_query(self, query: dict = None):
        validator = query.pop('v', 'https')
        count = int(query.pop('c', 1))
        downvote = query.popall('d', [])
        task = ProxyItemForWeb(
            meta={'validator': validator, 'count': count, 'downvote': downvote})
        yield task


if __name__ == "__main__":
    ProxyCrawler().run()
