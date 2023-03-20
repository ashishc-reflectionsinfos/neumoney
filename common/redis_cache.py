import json
import logging
import os
import sys
from flask import current_app as cp
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'common'))
from utilities import Utils
from string_table import AppMessages
from redis import Redis
from secret_manager import SecreteData


def redis_connection():
    try:
        cache = None
        if "redis_connection_cache" in cp.config and cp.config['redis_connection_cache'] is not None:
            cache = cp.config['redis_connection_cache']
        else:
            sec_key = SecreteData()
            host = sec_key.REDIS_SERVER
            port = sec_key.REDIS_PORT
            redis = Redis(host=host, decode_responses=True,
                      port=port)
            cp.config['redis_connection_cache'] = redis
            cache = cp.config['redis_connection_cache']

        return cache
    except Exception:
        raise Exception("Connected to Redis Failed")

class RedisCache:
    def __init__(self, logger):
        if logger:
            self.logger = logger

    def set_redis_cache(self, key, value):
        sec_key = SecreteData()
        prefix = sec_key.REDIS_PREFIX
        exp = int(sec_key.REDIS_EXPIRE)
        key = prefix + key
        success = True
        try:
            redis = redis_connection()
            if redis.ping():
                logging.info("SET REDIS CACHE | Connected to Redis")
                redis.set(key, json.dumps(value))
                redis.expire(key, exp)
        except Exception as excp:
            success = False
            Utils.process_exception(
                "SET REDIS CACHE",
                excp,
                self.logger,
                f'{AppMessages.INTERNAL_ERROR} during set_redis_cache',
                key
            )
        finally:
            self.logger.info("SET REDIS CACHE | completed set_redis_cache")
            #redis.close()
            return success

    def get_redis_cache(self, key, is_json=True):
        sec_key = SecreteData()
        prefix = sec_key.REDIS_PREFIX
        key = prefix + key
        success = True
        data = ''

        try:
            redis =  redis_connection()
            if redis.ping():
                logging.info("GET REDIS CACHE | Connected to Redis")

                if is_json:
                    data = redis.get(key)
                    if data:
                        data = json.loads(data)

                else:
                    data = redis.get(key)

        except Exception as exc:
            success = False
            Utils.process_exception(
                "GET REDIS CACHE", exc,
                self.logger,
                f'{AppMessages.INTERNAL_ERROR} during get_redis_cache',
                key
            )
        finally:
            self.logger.info("GET REDIS CACHE | completed get_redis_cache")
            #redis.close()
            return success, data

    def remove_redis_cache(self, key):
        sec_key = SecreteData()
        prefix = sec_key.REDIS_PREFIX
        key = prefix + key
        success = True
        data = ''
        try:
            redis =  redis_connection()
            if redis.ping():
                logging.info("REDIS_CACHE | Connected to Redis")
                data = redis.get(key)
                if data:
                    redis.delete(key)
        except Exception as excp:
            success = False
            Utils.process_exception(
                "REDIS", excp,
                self.logger,
                AppMessages.TRY_AGAIN,
                key
            )
        finally:
            self.logger.info("REDIS_CACHE | completed remove_redis_cache")
            #redis.close()
            return success, data
