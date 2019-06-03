from aproxy.validator import HTTPValidator, HTTPSValidator
MAX_REQUESTS_FOR_VALIDATOR = 100


# VALIDATORS = [HTTPValidator, HTTPSValidator]


# key is set for web query
VALIDATORS = {
    'http': HTTPValidator,
    'https': HTTPSValidator
}

# 15min
REVALIDATE_TIME = 15 * 60


SCORE_LIMIT = 2
SPEED_LIMIT = 10  # in second
TTL_LIMIT = 10 * 60  # in second
