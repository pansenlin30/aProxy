from aproxy.task import operate_on_66ip_page

COMMON_TASKS = [
    {
        'name': 'xici.com',
        'resource': ['http://www.xicidaili.com/nn/%s' % i for i in range(1, 6)] +
                    ['http://www.xicidaili.com/wn/%s' % i for i in range(1, 6)] +
                    ['http://www.xicidaili.com/wt/%s' %
                        i for i in range(1, 6)],
        'interval': 60 * 2,
        'enable':1,

    },
    {
        'name': 'kuaidaili.com',
        'resource': ['https://www.kuaidaili.com/free/inha/%s' % i for i in range(1, 6)] +
                    ['https://www.kuaidaili.com/proxylist/%s' %
                        i for i in range(1, 11)],
        'enable':1,
    },
    {
        'name': 'kxdaili.com',
        'resource': ['http://ip.kxdaili.com/ipList/{}.html'.format(i) for i in range(1, 11)],
        'enable':1,

    },
    {
        'name': 'ip3366.net',
        'resource': ['http://www.ip3366.net/free/?stype=1&page=%s' % i for i in range(1, 3)] +
                    ['http://www.ip3366.net/free/?stype=3&page=%s' %
                        i for i in range(1, 3)],
        'interval': 30,
        'enable':1,
    },
    {
        'name': '66ip.cn',
        'resource': ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)] +
                    ['http://www.66ip.cn/areaindex_%s/%s.html' % (i, j)
                     for i in range(1, 35) for j in range(1, 3)],
        'interval': 2 * 60,
        'browser': operate_on_66ip_page,
        'enable': 1,
    },
    {
        'name': 'mrhinkydink.com',
        'resource': ['http://www.mrhinkydink.com/proxies.htm'],
        'interval': 2 * 60,
        'enable':1,
    },
    {
        'name': 'iphai.com',
        'resource': [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wp',
            'http://www.iphai.com/'
        ],
        'enable': 1,
    },
    {
        'name': 'ab57.ru',
        'resource': ['http://ab57.ru/downloads/proxyold.txt'],
        'css_divider': '@text',
        'enable': 1,
    },

    {
        'name': 'proxylists.net',
        'resource': ['http://www.proxylists.net/http_highanon.txt'],
        'css_divider': '@text',
        'enable': 1,
    },
    {'name': 'my-proxy.com',
     'resource': [
         'https://www.my-proxy.com/free-proxy-list.html',
             'https://www.my-proxy.com/free-elite-proxy.html',
             'https://www.my-proxy.com/free-anonymous-proxy.html',
     ],
     'css_divider': '#list .list',
     'enable':1,

     },
    {'name': 'rmccurdy.com',
     'resource': [
             'https://www.rmccurdy.com/scripts/proxy/good.txt'
     ],
     'css_divider': '@text',
     'enable': 1
     },
    {
        'name': 'us-proxy.org',
        'resource': ['https://www.us-proxy.org/'],
        'enable':1,
    },
    {
        'name': 'sslproxies.org/',
        'resource': ['https://www.sslproxies.org/'],
        'enable': 1,
    },
]

TEST_TASKS = [
    {
        'name': '66ip.cn',
        'resource': ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)] +
                    ['http://www.66ip.cn/areaindex_%s/%s.html' % (i, j)
                     for i in range(1, 35) for j in range(1, 3)],
        'interval': 2 * 60,
        'browser': operate_on_66ip_page,
        'enable': 1,
    },

]
