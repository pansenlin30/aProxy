from acrawler.task import Task
from acrawler import Request, SkipTaskError
import random


class ProxyGen(Task):

    async def _execute(self):
        if self.meta.get('enable'):
            interval_s = self.meta.get('interval', 60) * 60
            for url in self.meta.get('resource', []):
                yield Request(url, priority=random.randint(0, 100), recrawl=interval_s)
        yield None
