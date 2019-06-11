from acrawler.task import Task
from acrawler import Request, Item, ParselItem, Parser
from acrawler.http import BrowserRequest
from parsel import Selector
import random
import re

PATTERN = re.compile(
    r'\D((?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))\D*(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[0-9]{1,4})')


def parse_text(text):
    for match in PATTERN.finditer(text):
        ip = match.groups()[0]
        port = match.groups()[1]
        proxy = ip + ':' + port
        yield ProxyItem(extra={'proxy': proxy})


def parse_text_response(response):
    yield from parse_text(response.text)


class ProxyItemForWeb(Item):
    pass


class ProxyItem(Item):
    pass


class ProxyParseItem(ParselItem):

    def custom_process(self, content):
        # text = self.sel.xpath("string(.)").get()
        text = self.sel.xpath(".").get()
        yield from parse_text(text)


class ProxyGen(Task):
    cb_table = {
        '@text': parse_text_response
    }

    async def _execute(self):
        if self.meta.get('enable'):
            interval_s = self.meta.get('interval', 60) * 60
            if 'browser' in self.meta:
                for url in self.meta.get('resource', []):
                    r = BrowserRequest(
                        url, page_callback=self.meta['browser'], recrawl=interval_s)
                    yield r
            else:
                cb = None
                if 'css_divider' in self.meta:
                    css_divider = self.meta['css_divider']
                    if not css_divider in self.cb_table:
                        self.cb_table[css_divider] = Parser(
                            css_divider=css_divider, item_type=ProxyParseItem).parse
                    cb = self.cb_table[css_divider]
                for url in self.meta.get('resource', []):
                    r = Request(url, priority=random.randint(
                        0, 100), callback=self.crawler.parse, recrawl=interval_s, status_allowed=[])
                    if cb:
                        r.add_callback(cb)
                    yield r
        yield None


async def operate_on_66ip_page(page, response):
    if response.status != 200:
        await page.waitForNavigation({'waitUntil': 'domcontentloaded'})
    main_sel = Selector(await page.text())
    for sel in main_sel.css('table tr'):
        yield ProxyParseItem(selector=sel)
    # for task in parse_text(await page.text()):
    #     yield task
    # await page.screenshot(show=True)
