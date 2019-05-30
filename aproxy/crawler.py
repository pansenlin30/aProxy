from acrawler import Crawler, get_logger, Parser, Request, ParselItem
from aproxy.rules import COMMON_TASKS
from aproxy.task import ProxyGen
from aproxy.handlers import *
import re

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
        'DOWNLOAD_DELAY': 0.5,
        'MAX_REQUESTS_PER_HOST': 1,
    }

    parsers = [Parser(css_divider='table tr', item_type=ProxyItem),
                Parser(css_divider='li ul', item_type=ProxyItem),]

    async def start_requests(self):
        for info in COMMON_TASKS:
            yield ProxyGen(meta=info)


if __name__ == "__main__":
    ProxyCrawler().run()
