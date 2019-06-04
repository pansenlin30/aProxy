import re
import time

from acrawler import Crawler, ParselItem, Parser, Request, get_logger, Item, register
from aproxy.rules import TEST_TASKS
from aproxy.task import ProxyGen, ProxyItemForWeb, ProxyParseItem
import asyncio
import sys
import os

logger = get_logger('aproxy')

PATTERN = re.compile(
    r'\b((?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))\D*(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})')


@register(family='ProxyItem', position=2)
def log_item(item):
    if 'proxy' in item:
        logger.info(item['proxy'])


class TestCrawler(Crawler):

    config = {
        'DOWNLOAD_DELAY': 1,
        'MAX_REQUESTS_PER_HOST': 1,
        'MAX_REQUESTS': 8,
    }

    middleware_config = {
        'aproxy.handlers.AddCookie': 500,
    }

    parsers = [Parser(css_divider='table tr', item_type=ProxyParseItem),
               Parser(css_divider='li ul', item_type=ProxyParseItem), ]

    async def start_requests(self):
        for info in TEST_TASKS:
            yield ProxyGen(meta=info)

    async def parse(self, resp):
        pass


if __name__ == "__main__":
    TestCrawler().run()
