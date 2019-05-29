from acrawler.task import Task
from acrawler import Request, SkipTaskError
import random
class ProxyGen(Task):

    def __init__(self, dont_filter=True, priority=0, meta=None, family=None, recrawl=0, exetime=0):
        super().__init__(dont_filter=dont_filter, priority=priority, meta=meta, family=family, recrawl=recrawl, exetime=exetime)

    async def _execute(self):
        if self.meta.get('enable'):
            for url in self.meta.get('resource',[]):
                yield Request(url, priority=random.randint(0,100))
        yield None

