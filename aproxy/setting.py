from aproxy.validator import HTTPValidator, HTTPSValidator
MAX_REQUESTS_FOR_VALIDATOR = 100


VALIDATORS = [HTTPValidator, HTTPSValidator]

# 15min
REVALIDATE_TIME = 15*60
