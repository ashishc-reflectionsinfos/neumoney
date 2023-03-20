
import requests
import os
import sys
from app_response import AppResponse
from secret_manager import SecreteData
from status_codes import StatusCode
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'common'))
from utilities import Utils
from string_table import AppMessages
from log_data import ApplicationLogger as applog


def get_user_profile_by_uuid(uuid):
    """
    This is a wrapper function to call identity/get-userprofile-by-uuid?user_uuid=05ebc178-64a9-11ed-bc69-619df24c39c7
     to get user profile details.
    :param
        headers_data:
                Content-Type, Authorization:Bearer + JWT token
    :return:
        app_response with JSON data of profile details
    """
    key = SecreteData()
    app_response = AppResponse()
    try:
        applog.info("GET USER PROFILE BY UUID | Sending request to identity "
                    "get-userprofile-by-uuid to get user data")
        url = key.INTERNAL_BASE_URL + "/identity/get-user-profile-by-uuid/"
        params = {
            "user_uuid": uuid
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer ' + key.IDENTITY_JWT_TOKEN
        }
        applog.info(f"GET USER PROFILE BY UUID | started calling url {url}")
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == StatusCode.SUCCESS:
            applog.info(f"GET USER PROFILE BY UUID | Request successful with response 200")
            app_response_1 = response.json()
            app_response['data']['first_name'] = app_response_1['data']['firstName']
            app_response['data']['last_name'] = app_response_1['data']['lastName']
            app_response['data']['email_id'] = app_response_1['data']['email']
            app_response['data']['phone_number'] = app_response_1['data']['phoneNumber']
            app_response['data']['authorization_token'] = app_response_1['data']['authorizationToken']
            app_response['data']['phone_verified'] = app_response_1['data']['phoneVerified']
            app_response['data']['email_verified'] = app_response_1['data']['emailVerified']
            app_response['code'] = StatusCode.SUCCESS
            app_response['message'] = AppMessages.SUCCESS
            app_response['status'] = AppMessages.TRUE
        else:
            applog.error(f"GET USER PROFILE BY UUID | Request Failed with response {response.status_code, response.content}")
            app_response.set_response(StatusCode.INTERNAL_SERVER_ERROR, {}, AppMessages.FETCH_USER_DATA_FAILED,
                                      AppMessages.FALSE)
    except Exception as exp:
        applog.error(f"GET USER PROFILE BY UUID | Error while get_user_profile_by_uuid   {exp.args}")
        Utils.process_exception(
            'GET USER PROFILE BY UUID',
            exp,
            applog,
            AppMessages.TRY_AGAIN,
            app_response
        )
    finally:
        applog.info("GET USER PROFILE BY UUID | Completed get_adress_by_uuid")
        return app_response

