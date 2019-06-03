from multiprocessing import Process
from multiprocessing.pool import Pool
from aproxy.crawler import ProxyCrawler
from aproxy.setting import VALIDATORS
import signal


def run_crawler(c_cls):
    c = c_cls()
    c.run()


if __name__ == "__main__":
    cproc = Process(target=run_crawler, args=(ProxyCrawler,))
    cproc.start()
    procs = [cproc]
    for vcls in VALIDATORS.values():
        proc = Process(target=run_crawler, args=(vcls,))
        proc.start()
        procs.append(proc)
    print('aProxy starts working...')

    try:
        cproc.join()
    except KeyboardInterrupt:
        for proc in procs:
            proc.join()
        print('\nProxy is stopped.')
