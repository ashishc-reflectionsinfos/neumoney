from functools import wraps
import os
import sys
import requests
import jwt
from flask import request, make_response, jsonify
from marshmallow import Schema, fields, validate, ValidationError

from secret_manager import SecreteData
from string_table import AppMessages
from logger_utils import get_request_id
from status_codes import StatusCode

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'common'))
from log_data import ApplicationLogger as applog


class ValidateHeadersSchema(Schema):
    deviceType = fields.String(required=True)
    appVersion = fields.String(required=True)
    ContentType = fields.String(required=True)
    deviceId = fields.UUID(required=True)
    device = fields.String(required=True)
    Authorization = fields.String(required=True, validate=validate.Length(min=10))
    deviceVersion = fields.String(required=False, allow_none=True)
    ipAddress = fields.String(required=False, allow_none=True)
    bundleId = fields.String(required=False, allow_none=True)


def token_required(f):
    """
    Function used to validate token
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        key = SecreteData()
        applog.info("TOKEN REQUIRED | Going to validate header")
        try:
            headers = {
                "deviceType": request.headers.get("deviceType"),
                "appVersion": request.headers.get("appVersion"),
                "ContentType": request.headers.get("Content-Type"),
                "deviceId": request.headers.get("deviceId"),
                "device": request.headers.get("device"),
                "Authorization": request.headers.get("Authorization"),
                "deviceVersion": request.headers.get("deviceVersion"),
                "ipAddress": request.headers.get("ipAddress"),
                "bundleId": request.headers.get("bundleId")

            }
            headers_schema = ValidateHeadersSchema()
            headers_validate = headers_schema.load(headers)
            token_auth = headers_validate.get("Authorization")
            if "Bearer" not in token_auth:
                return {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.SESSION_TIME_OUT,
                        'status': False}
            else:
                access_token = token_auth.split()[1]
                token = jwt.decode(access_token, options={"verify_signature": False, "verify_exp": True})
                auth_id = token['sub'].split('|')[1]
                from redis_cache import RedisCache
                redis_obj = RedisCache(applog)
                status, user = redis_obj.get_redis_cache(auth_id, True)
                if status and user:
                    if access_token == user["authorization_token"]:
                        if user['email_verified'] and user['phone_verified']:
                            pass
                        else:
                            raise Exception
                    else:
                        raise Exception
                else:
                    url = key.BASE_URL + "/identity/check-token"
                    payload = {'accessToken': access_token}
                    headers = {
                        'content-type': 'application/json',
                        'x-request-referral-Id': get_request_id()
                    }
                    applog.info("TOKEN REQUIRED | going to validate token by calling /identity/check-token")
                    response = requests.request("POST", url, headers=headers, json=payload)
                    response = response.json()
                    if response['code'] == StatusCode.SUCCESS:
                        pass
                    else:
                        response = {'code': response['code'], 'data': {}, 'message': response['message'],
                                    'status': False}
                        return make_response(jsonify(response), response['code'])
        except jwt.ExpiredSignatureError:
            response = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {},
                        'message': AppMessages.SESSION_TIME_OUT,
                        'status': False}
            return make_response(jsonify(response), response['code'])
            applog.info("TOKEN REQUIRED | Signature error")
        except ValidationError as ve:
            response = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.SESSION_TIME_OUT,
                        'status': False}
            applog.info(f"TOKEN REQUIRED | Validation error occurred {ve}")
            return make_response(jsonify(response), response['code'])
        except Exception as exp:
            applog.info(f"TOKEN REQUIRED | {exp}")
            response = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.SESSION_TIME_OUT,
                        'status': False}
            return make_response(jsonify(response), response['code'])
        except requests.exceptions.RequestException as e:
            response = {'code': StatusCode.INTERNAL_SERVER_ERROR, 'data': {}, 'message': AppMessages.TRY_AGAIN,
                        'status': False}
            return make_response(jsonify(response), response['code'])
        return f(*args, **kwargs)

    return decorator
