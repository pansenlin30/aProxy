
COMMON_TASKS = [
    {
        'name': 'xici',
        'test': 'xicidaili.com',
        'resource': ['http://www.xicidaili.com/nn/%s' % i for i in range(1, 6)] +
                    ['http://www.xicidaili.com/wn/%s' % i for i in range(1, 6)] +
                    ['http://www.xicidaili.com/wt/%s' %
                        i for i in range(1, 6)],
        'enable':1,

    },
    {
        'name': 'kuaidaili',
        'test': None,
        'resource': ['https://www.kuaidaili.com/free/inha/%s' % i for i in range(1, 6)] +
                    ['https://www.kuaidaili.com/proxylist/%s' %
                        i for i in range(1, 11)],
        'enable':1,
    },
    {
        'name':'kxdaili',
        'resource': ['http://ip.kxdaili.com/ipList/{}.html'.format(i) for i in range(1, 11)],
        'enable':1,

    },
    {
        'name': 'ip3366.net',
        'resource': ['http://www.ip3366.net/free/?stype=1&page=%s' % i for i in range(1, 3)] +
                    ['http://www.ip3366.net/free/?stype=3&page=%s' % i for i in range(1, 3)],
        'interval': 30,
        'enable':1,
    },
    {
        'name': 'mrhinkydink.com',
        'resource': ['http://www.mrhinkydink.com/proxies.htm'],
        'interval': 2 * 60,
        'enable':1,
    },
]
