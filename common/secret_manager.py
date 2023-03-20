import json
import os

import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from flask import current_app as cp

from parameter_store import get_parameter_values


def SecretKeys():
    """
    This function make connection with aws secret manager and create a SecretCacheConfig object
    :return:
        SecretCache object
    """
    try:
        session = boto3.session.Session()
        if os.getenv("environment") == "local":
            client = session.client(os.getenv("aws_secrete_manager_service"),
                                    region_name=os.getenv("aws_secrete_manager_region"),
                                    aws_access_key_id=os.getenv("aws_access_key"),
                                    aws_secret_access_key=os.getenv("aws_secret_access_key"))

        else:
            client = session.client(os.getenv("aws_secrete_manager_service"),
                                    region_name=os.getenv("aws_secrete_manager_region"))

        cache_config = SecretCacheConfig(secret_refresh_interval=int(os.getenv("secret_refresh_interval")))

        cache = SecretCache(config=cache_config, client=client)

        return cache

    except Exception:
        raise


def get_secret_values():
    """
    This function take secretCache object from app config, if it's not there then call SecretKeys function and get the
    object,
    Using that object it will call aws secret manager and get the all keys and values in dictionary form.
    :return:
        Dictionary of secret keys and values
    """
    try:
        if "secret_cache" in cp.config and cp.config['secret_cache'] is not None:
            cache = cp.config['secret_cache']
        else:
            cp.config['secret_cache'] = SecretKeys()
            cache = cp.config['secret_cache']

        Secret = cache.get_secret_string(os.getenv("aws_secrete_manager_service_id"))

        return json.loads(Secret)
    except Exception:
        raise


class SecreteData:
    """
    This class assign all the secrete values and parameter store values to the variables
    """

    def __init__(self):
        SECRET = get_secret_values()
        PARAMETER = get_parameter_values()

        self.PORT = PARAMETER["APPLICATION_PORT"]
        self.DB_USER = SECRET["DB_CREDIT_LIMIT_USER"]
        self.DB_PASS = SECRET["DB_CREDIT_LIMIT_PASSWORD"]
        self.DB_HOST = SECRET["DB_HOST"]
        self.DB_DRIVER = PARAMETER["DB_DRIVER"]
        self.ADMIN_DB_NAME = SECRET["ADMIN_DB_NAME"]
        self.ADMIN_DB_SCHEMA = PARAMETER["ADMIN_SCHEMA"]
        self.IDENTITY_DB_NAME = SECRET["IDENTITY_DB_NAME"]
        self.IDENTITY_SCHEMA = PARAMETER["IDENTITY_SCHEMA"]
        self.CREDIT_CARD_DB_NAME = SECRET["CREDIT_CARD_DB_NAME"]
        self.CREDIT_CARD_SCHEMA = PARAMETER["CREDIT_CARD_SCHEMA"]
        self.CREDIT_LIMIT_DB_NAME = SECRET["CREDIT_LIMIT_DB_NAME"]
        self.CREDIT_LIMIT_SCHEMA = PARAMETER["CREDIT_LIMIT_SCHEMA"]
        self.NOTIFICATION_DB_NAME = SECRET["NOTIFICATION_DB_NAME"]
        self.NOTIFICATION_SCHEMA = PARAMETER["NOTIFICATION_SCHEMA"]
        self.ONBOARDING_DB_NAME = SECRET["ONBOARDING_DB_NAME"]
        self.ONBOARDING_SCHEMA = PARAMETER["ONBOARDING_SCHEMA"]
        self.REPAYMENT_DB_NAME = SECRET["REPAYMENT_DB_NAME"]
        self.REPAYMENT_SCHEMA = PARAMETER["REPAYMENT_SCHEMA"]
        self.REWARDS_DB_NAME = SECRET["REWARDS_DB_NAME"]
        self.REWARDS_SCHEMA = PARAMETER["REWARDS_SCHEMA"]
        self.AUTH_TOKEN = SECRET["AUTH_TOKEN"]
        self.ACCOUNT_SID = SECRET["ACCOUNT_SID"]
        self.MESSAGE_SERVICE_ID = SECRET["MESSAGE_SERVICE_ID"]
        self.AUTH0_CLIENT_ID = SECRET["AUTH0_CLIENT_ID"]
        self.AUTH0_CLIENT_SECRET = SECRET["AUTH0_CLIENT_SECRET"]
        self.AUTH0_CONNECTION = SECRET["AUTH0_CONNECTION"]
        self.MASTER_OTP = PARAMETER["MASTER_OTP"]
        self.POOL_SIZE = PARAMETER["POOL_SIZE"]
        self.SEND_OTP = PARAMETER["SEND_OTP"]
        self.REDIS_SERVER = SECRET["REDIS_SERVER"]
        self.REDIS_PORT = PARAMETER["REDIS_PORT"]
        self.LOG_ENABLED = PARAMETER["LOG_ENABLED"]
        self.ALLOY_JOURNEY_TOKEN = SECRET["ALLOY_JOURNEY_TOKEN"]
        self.ALLOY_BASE_URL = SECRET["ALLOY_BASE_URL"]
        self.ALLOY_USERNAME = SECRET["ALLOY_USERNAME"]
        self.ALLOY_PASSWORD = SECRET["ALLOY_PASSWORD"]
        self.PERSONA_INQUIRY_TEMPLATE_ID = SECRET["PERSONA_INQUIRY_TEMPLATE_ID"]
        self.PERSONA_BASE_URL = SECRET["PERSONA_BASE_URL"]
        self.CROSSRIVER_ID = SECRET["CROSSRIVER_ID"]
        self.CROSSRIVER_SECRET = SECRET["CROSSRIVER_SECRET"]
        self.CROSSRIVER_AUDIENCE = SECRET["CROSSRIVER_AUDIENCE"]
        self.CROSSRIVER_IDEMPOTENCY = SECRET["CROSSRIVER_IDEMPOTENCY"]
        self.CROSSRIVER_PARTNER_ID = SECRET["CROSSRIVER_PARTNER_ID"]
        self.FINICITY_URL = SECRET["FINICITY_URL"]
        self.FINICITY_PARTNER_ID = SECRET["FINICITY_PARTNER_ID"]
        self.FINICITY_PARTNER_SECRET = SECRET["FINICITY_PARTNER_SECRET"]
        self.FINICITY_APP_KEY = SECRET["FINICITY_APP_KEY"]
        self.FINICITY_EXPERIENCE = SECRET["FINICITY_EXPERIENCE"]
        self.FINICITY_WEBHOOK = SECRET["FINICITY_WEBHOOK"]
        self.SCIENAPTIC_BASE_URL = SECRET["SCIENAPTIC_BASE_URL"]
        self.I2C_BASE_URL = SECRET["I2C_BASE_URL"]
        self.I2C_ID = SECRET["I2C_ID"]
        self.I2C_USER_ID = SECRET["I2C_USER_ID"]
        self.I2C_PASSWORD = SECRET["I2C_PASSWORD"]
        self.I2C_CARD_STARTING_NUMBER = SECRET["I2C_CARD_STARTING_NUMBER"]
        self.I2C_CARD_PROGRAMME_ID = SECRET["I2C_CARD_PROGRAMME_ID"]
        self.PERSONA_API_KEY = SECRET["PERSONA_API_KEY"]
        self.BASE_URL = SECRET["BASE_URL"]
        self.PRODUCT = PARAMETER["PRODUCT"]
        self.LOAN_TYPE = PARAMETER["LOAN_TYPE"]
        self.ONBOARDING_JWT_TOKEN = SECRET['ONBOARDING_JWT_TOKEN']
        self.ONBOARDING_JWT_SECRET = SECRET['ONBOARDING_JWT_SECRET']
        self.IDENTITY_JWT_TOKEN = SECRET['IDENTITY_JWT_TOKEN']
        self.IDENTITY_JWT_SECRET = SECRET['IDENTITY_JWT_SECRET']
        self.KYC_JWT_TOKEN = SECRET['KYC_JWT_TOKEN']
        self.KYC_JWT_SECRET = SECRET['KYC_JWT_SECRET']
        self.CREDIT_CARD_JWT_TOKEN = SECRET['CREDIT_CARD_JWT_TOKEN']
        self.CREDIT_CARD_JWT_SECRET = SECRET['CREDIT_CARD_JWT_SECRET']
        self.CC_LIMIT_JWT_TOKEN = SECRET['CC_LIMIT_JWT_TOKEN']
        self.CC_LIMIT_JWT_SECRET = SECRET['CC_LIMIT_JWT_SECRET']
        self.REPAYMENT_JWT_TOKEN = SECRET['REPAYMENT_JWT_TOKEN']
        self.REPAYMENT_JWT_SECRET = SECRET['REPAYMENT_JWT_SECRET']
        self.NOTIFICATION_JWT_TOKEN = SECRET['NOTIFICATION_JWT_TOKEN']
        self.NOTIFICATION_JWT_SECRET = SECRET['NOTIFICATION_JWT_SECRET']
        self.SENSIBLE_DATA = PARAMETER["SENSIBLE_DATA"]
        self.REDIS_PREFIX = os.getenv('redis_prefix')
        self.CREDIT_APPROVED_SNS_ARN = SECRET["CREDIT_APPROVED_SNS_ARN"]
        self.SNS_SUBJECT_CREDIT_APPROVED = "credit_approved"
        self.INTERNAL_BASE_URL = SECRET["INTERNAL_BASE_URL"]
        self.SCIENAPTICS_APPROVED_DECISION = "Approve"
        self.SCIENAPTICS_DECLINED_DECISION = "Decline"
        self.SCIENAPTICS_FREEZE_DECISION = "App Not Decisioned: Freeze on File"
        self.SCIENAPTICS_FREEZE_STAGE_ID = 40
        self.SKIP_CODES = [401, 403, 404, 405, 429, 502, 503, 504]
        self.SCIENAPTIC_TOKEN = SECRET["SCIENAPTIC_AUTH_TOKEN"]
        self.THIRD_PARTY_LOG_ENABLED = PARAMETER["THIRD_PARTY_LOG_ENABLED"]
        self.TU_RAW_DATA_FOLDER = PARAMETER["TU_RAW_DATA_FOLDER"]
        self.REDIS_EXPIRE = PARAMETER["REDIS_EXPIRE"]
        self.THIRD_PARTY_LOGGING_SERVICE = SECRET["THIRD_PARTY_LOGGING_SERVICE"]
        self.ADMIN_DATA_SYNC_SNS_ARN = SECRET["ADMIN_DATA_SYNC_SNS_ARN"]
        self.THIRD_PARTY_LOGGING_SNS_ARN = SECRET["THIRD_PARTY_LOGGING_SNS_ARN"]