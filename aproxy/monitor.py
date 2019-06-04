from prometheus_client import start_http_server
from prometheus_client.core import (
    CounterMetricFamily, GaugeMetricFamily,
    REGISTRY
)
import aioredis
from aproxy.setting import EXPORTER_LISTEN_HOST, EXPORTER_LISTEN_PORT
from acrawler import Crawler
import time
import asyncio


class MonitorCrawler(Crawler):
    pass


class CustomCollector:
    def __init__(self, name):
        # self.redis = asyncio.run()
        self.crawler = MonitorCrawler()
        self.name = name
        self.loop = asyncio.new_event_loop()
        self.redis = self.loop.run_until_complete(
            aioredis.create_redis_pool('redis://localhost'))
        key_names = ['init', 'tmp', 'last', 'speed', 'score']

        # get five redis keys
        self.keys = {
            k: 'aproxy:' + self.name + ':' + k for k in key_names
        }
        self.pq_key = 'acrawler:' + self.name + ':' + 'q:pq'
        self.score_limit = self.crawler.config.get('SCORE_LIMIT')
        self.speed_limit = self.crawler.config.get('SPEED_LIMIT')
        self.ttl_limit = self.crawler.config.get('TTL_LIMIT')

    def collect(self):
        start_time = int(time.time()) - self.ttl_limit
        tr = self.redis.multi_exec()
        tr.scard(self.keys['init'])
        tr.zcard(self.pq_key)
        tr.zrevrangebyscore(self.keys['score'], min=self.score_limit)
        tr.zrevrangebyscore(self.keys['last'], min=start_time)
        tr.zrangebyscore(self.keys['speed'], 0,
                         1000*self.speed_limit)
        tr.zcard('acrawler:ProxyCrawler:q:pq')
        r = self.loop.run_until_complete(tr.execute())
        available_proxies = len(set(r[2]) & set(r[3]) & set(r[4]))

        yield GaugeMetricFamily('init_proxies', 'a', r[0])
        yield GaugeMetricFamily('to_validated_proxies', 'proxies to validate', r[1])
        yield GaugeMetricFamily('scored_proxies', 'high score proxies', len(r[2]))
        yield GaugeMetricFamily('alive_proxies', 'proxies validated recently', len(r[3]))
        yield GaugeMetricFamily('speed_proxies', 'high speed proxies', len(r[4]))
        yield GaugeMetricFamily('available_proxies', 'proxies of high quality', available_proxies)
        yield GaugeMetricFamily('to_crawled_pages', 'total pages to crawl', r[5])


def run_monitor():
    REGISTRY.register(CustomCollector('HTTPSValidator'))
    start_http_server(EXPORTER_LISTEN_PORT, addr=EXPORTER_LISTEN_HOST)
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_monitor()
