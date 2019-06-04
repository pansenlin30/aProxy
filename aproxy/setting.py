from aproxy.validator import HTTPValidator, HTTPSValidator
MAX_REQUESTS_FOR_VALIDATOR = 100


# VALIDATORS = [HTTPValidator, HTTPSValidator]


# key is set for web query
VALIDATORS = {
    'http': HTTPValidator,
    'https': HTTPSValidator
}

# 15min
REVALIDATE_TIME = 10 * 60


SCORE_LIMIT = 2
SPEED_LIMIT = 10  # in second
TTL_LIMIT = 15 * 60  # in second


WEB_HOST = 'localhost'
WEB_PORT = 8079


EXPORTER_LISTEN_HOST = 'localhost'
EXPORTER_LISTEN_PORT = 8000
