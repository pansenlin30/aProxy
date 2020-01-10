from aproxy.validator import HTTPValidator, HTTPSValidator

MAX_REQUESTS_FOR_VALIDATOR = 200


# VALIDATORS = [HTTPValidator, HTTPSValidator]


# key is set for web query
VALIDATORS = {
    # 'http': HTTPValidator,
    "https": HTTPSValidator,
}

# 10min
REVALIDATE_TIME = 15 * 60

DISABLE_COOKIES = True

SCORE_LIMIT = 2
SPEED_LIMIT = 10  # in second
TTL_LIMIT = 15 * 60  # in second


WEB_HOST = "localhost"
WEB_PORT = 8002


EXPORTER_LISTEN_HOST = "localhost"
EXPORTER_LISTEN_PORT = 8001

REQUEST_CONFIG = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    },
}
