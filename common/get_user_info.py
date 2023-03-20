import requests

from app_response import AppResponse
from log_data import ApplicationLogger as applog
from logger_utils import get_request_id
from redis_cache import RedisCache
from secret_manager import SecreteData
from status_codes import StatusCode
from string_table import AppMessages
from utilities import Utils, get_auth_id_from_token


def get_user_info(headers):
    """
    This is a wrapper function to call identity/get-user-info
     to get user profile details.
    :param
        headers_data:headers

    :return:
        app_response with JSON data of profile details
    """
    key = SecreteData()
    app_response = AppResponse()
    get_data = {}
    try:
        applog.info("GET USER INFO | Sending request to identity "
                    "get-user-info to get user data")
        url = key.BASE_URL + "/identity/get-user-info/"
        applog.info(f"GET USER INFO | started calling url {url}")
        headers = {
            "Authorization": headers.get("Authorization"),
            'x-request-referral-Id': get_request_id()
        }
        response = requests.post(url, headers=headers)
        if response.status_code == StatusCode.SUCCESS:
            applog.info(f"GET USER INFO | Request successful with response 200")
            user_data = response.json()
            get_data['first_name'] = user_data['data']['firstName']
            get_data['last_name'] = user_data['data']['lastName']
            get_data['email_id'] = user_data['data']['email']
            get_data['phone_number'] = user_data['data']['phoneNumber']
            get_data['authorization_token'] = headers["Authorization"].split(" ")[-1]
            get_data['phone_verified'] = user_data['data']['phoneVerified']
            get_data['email_verified'] = user_data['data']['emailVerified']
            get_data['user_uuid'] = user_data['data']['userUuid']
        else:
            applog.error(f"GET USER INFO | Request Failed with response {response.status_code, response.content}")
    except Exception as exp:
        applog.error(f"GET USER INFO | Error while get_user_info   {exp.args}")
        Utils.process_exception(
            'GET USER INFO',
            exp,
            applog,
            AppMessages.TRY_AGAIN,
            app_response
        )
    finally:
        applog.info("GET USER INFO | Completed get_user_info")
        return get_data


def get_user_info_from_redis(headers):
    """ To get user  info from redis cache
        if cache fails call identity/get user info API to take user details
        Args:
             accepts auth0_id
        Returns:
            return status true and user details if user details exists
            else return false status and no details
        """

    applog.info('GET USER INFO FROM REDIS | get_user_info')
    app_response = AppResponse()
    get_data = {}
    try:
        auth_token = headers['Authorization']
        auth0_id = get_auth_id_from_token(auth_token)
        applog.info("GET USER INFO FROM REDIS | Sending request to redis to get user data")
        redis_obj = RedisCache(applog)
        get_status, get_data = redis_obj.get_redis_cache(auth0_id, True)
        if get_status and (get_data is not None and get_data != ''):
            applog.info(
                f"GET USER INFO FROM REDIS | user information already resent in redis")
        else:
            applog.info(
                f"GET USER INFO FROM REDIS | calling identity get user info API for getting user profile details")
            get_data = get_user_info(headers)
    except Exception as exp:
        applog.error(f"GET USER INFO FROM REDIS | Error while fetching user data from redis{exp.args}")
        Utils.process_exception(
            "GET USER INFO FROM REDIS", exp,
            applog,
            AppMessages.TRY_AGAIN,
            app_response
        )
    finally:
        return get_data
