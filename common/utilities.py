from flask import current_app as cp, make_response, jsonify, request
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import traceback
from functools import wraps

import jwt
import requests
from marshmallow import ValidationError
from string_table import AppMessages
from app_response import AppResponse
from log_data import ApplicationLogger as applog
from secret_manager import SecreteData
from status_codes import StatusCode
import os
from logger_utils import get_request_id


class Utils:
    @staticmethod
    def process_exception(source, excp, logger, message, result, status='false', status_code=500):
        logger.error(message)
        logger.error(f'{source} | {traceback.format_exc()}')
        stack_trace = traceback.format_exc()
        resp = AppResponse(status_code, {}, message, status)
        for k in resp:
            result[k] = resp[k]

    @staticmethod
    def isTokenValid(access_token):
        try:
            access_token = access_token.split()
            message = 'INVALID'
            if "Bearer" in access_token:
                access_token = access_token[1]
                jwt.decode(access_token, options={"verify_signature": False, "verify_exp": True})
                message = access_token
        except jwt.ExpiredSignatureError:
            message = 'EXPIRED'
        except ValidationError as ve:
            message = 'INVALID'
        except Exception as exp:
            message = 'INVALID'
        finally:
            return message

    @staticmethod
    def get_log_config_path():
        key = SecreteData()
        # return configuring log path
        configPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  'config')
        log_var = int(key.LOG_ENABLED)
        if log_var == 1:  # writing to console
            configFile = configPath + '/LogConfigWeb.json'
        elif log_var == 2:  # writing to file
            configFile = configPath + '/LogConfigWeb1.json'
        elif log_var == 3:  # both writing to file and console
            configFile = configPath + '/LogConfigWeb2.json'
        else:  # default writing to console
            configFile = configPath + '/LogConfigWeb.json'

        return configFile


def get_redis_health(app_response, applog):
    """
        This function returns the health stat response for redis
        :param app_response: this response is modified
        :param applog: for logging
        :return: modified app_response
        """
    sec_key = SecreteData()
    host = sec_key.REDIS_SERVER
    port = sec_key.REDIS_PORT

    try:
        # applog.info("HEALTH CHECK | pinging to redis server")
        redis = Redis(host=host, decode_responses=True,
                      port=port)

        if redis.ping():
            # applog.info("HEALTH CHECK | pinged redis server")
            app_response['redis_code'] = StatusCode.SUCCESS
            app_response['redis_message'] = 'successfully connected to redis server !'
            app_response['redis_status'] = True

        else:
            applog.info("HEALTH CHECK | could not ping redis server")
            app_response['redis_code'] = StatusCode.INTERNAL_SERVER_ERROR
            app_response['redis_message'] = 'could not connect to redis server !'
            app_response['redis_status'] = False

    except Exception as excp:
        applog.error("HEALTH CHECK | " + str(excp))
        app_response['redis_code'] = StatusCode.INTERNAL_SERVER_ERROR
        app_response['redis_message'] = 'SOMETHING WENT WRONG'
        app_response['redis_status'] = False

    return app_response


def get_sql_health(app_response, applog):
    """
    This function returns the health stat response for SQL
    :param app_response: this response is modified
    :param applog: for logging
    :return: modified app_response
    """
    key = SecreteData()
    sql_client_driver = key.DB_DRIVER
    conn_string = sql_client_driver \
                  + key.DB_USER \
                  + ":" + key.DB_PASS \
                  + "@" + key.DB_HOST \
                  + "/" + key.CREDIT_LIMIT_DB_NAME

    engine = None

    try:
        # if "engine" in cp.config and cp.config['engine'] is not None:
        #     engine = cp.config['engine']
        # else:
        engine = create_engine(conn_string, pool_size=int(key.POOL_SIZE),
                               connect_args={
                                   'options': '-csearch_path={}'.format(str(key.CREDIT_LIMIT_SCHEMA))})
        cp.config["engine"] = engine

        # applog.info("HEALTH CHECK | Connection to SQL started")
        connection = engine.connect()
        session = Session(connection)

        if session is not None:
            app_response["sql_code"] = StatusCode.SUCCESS
            app_response["sql_message"] = 'SQL session successfully created'  # UserRegisterMessages.USER_FETCH_SUCCESS
            app_response["sql_status"] = True  # UserRegisterMessages.TRUE
            # applog.info("HEALTH CHECK | Connection to SQL DB established")

            session.close()
            connection.close()

        else:
            app_response["sql_code"] = StatusCode.INTERNAL_SERVER_ERROR
            app_response["sql_message"] = 'SQL session could not be created'  # UserRegisterMessages.QUERY_SUCCESS
            app_response["sql_status"] = False  # UserRegisterMessages.TRUE
            applog.info("HEALTH CHECK | Connection to SQL DB not established")

    except Exception as excp:
        applog.error("HEALTH CHECK | " + str(excp))
        app_response['sql_code'] = StatusCode.INTERNAL_SERVER_ERROR
        app_response['sql_message'] = 'SOMETHING WENT WRONG'
        app_response['sql_status'] = False

    return app_response


def get_health_check(app_response={}):
    """
    this function returns the JSON response for SQL and REDIS health stats
    :param app_response: response to be modified
    :return: modified app response
    """
    app_response['redis'] = get_redis_health({}, applog)
    # applog.info(f"HEALTH CHECK | completed redis health_check ")
    app_response['SQL'] = get_sql_health({}, applog)
    # applog.info(f"HEALTH CHECK | completed sql health_check ")

    return app_response


def check_health(f):
    """
    decorator for getting redis and sql health

    :param f: function with empty response
    :return: function with modified response
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        app_response = {}
        app_response['data'] = get_health_check()

        if app_response['data']['SQL']['sql_status'] * app_response['data']['redis']['redis_status'] == True:
            app_response = {'code': StatusCode.SUCCESS,
                            'data': app_response['data'],
                            'message': "Health Check Successfully Completed !",
                            'status': True}

            # applog.info("HEALTH CHECK | database connection successful")

        else:
            # applog.error("HEALTH CHECK | database connection unsuccessful")
            app_response = {'code': StatusCode.INTERNAL_SERVER_ERROR,
                            'data': app_response['data'],
                            'message': 'Could not establish connection to database',
                            'status': False}

        return f(app_response=app_response)

    return decorated


def headers_validation(headers_data):
    keys = SecreteData()
    app_response = AppResponse()
    try:
        applog.info("HEADER VALIDATION | Going to validate header")
        header = {
            "deviceType": headers_data.get("deviceType"),
            "appVersion": headers_data.get("appVersion"),
            "Content-Type": headers_data.get("Content-Type"),
            "deviceId": headers_data.get("deviceId"),
            "device": headers_data.get("device"),
            "Authorization": headers_data.get("Authorization"),
            'x-request-referral-Id': get_request_id()
        }

        token = headers_data["Authorization"]
        url = keys.BASE_URL + "/identity/check-token"
        access_token = token.split()
        if "Bearer" in access_token:
            data = access_token[1]
        else:
            data = access_token
        payload = {'accessToken': data}
        applog.info("HEADER VALIDATION | going to validate token by calling /identity/check-token")
        response = requests.post(url, headers=header, json=payload)
        app_response = response.json()
    except Exception as exp:
        Utils.process_exception(
            "HEADER VALIDATION",
            exp,
            applog,
            f' Exception occurred during headers_validation',
            app_response
        )

    finally:
        return app_response


def jwt_validation_internal(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        secret = SecreteData()
        key = secret.CC_LIMIT_JWT_SECRET
        headers = request.headers
        token = None
        if 'Authorization' in headers:
            bearer = headers.get('Authorization')
            token = bearer.split()[1]
        if not token:
            resp = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.UNAUTHORIZED_REQUEST,
                    'status': False}
            return make_response(jsonify(resp), resp['code'])
        try:
            data = jwt.decode(token, key, algorithms=["HS256"])
            applog.info("JWT VALIDATION INTERNAL | Authentication completed successfully")
        except jwt.ExpiredSignatureError as exp:
            applog.error("JWT VALIDATION INTERNAL | Expired jwt token received :" + str(exp))
            resp = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.AUTHENTICATION_FAILED,
                    'status': False}
            return make_response(jsonify(resp), resp['code'])
        except jwt.exceptions.InvalidSignatureError as exp:
            applog.error("JWT VALIDATION INTERNAL | Invalid jwt token received :" + str(exp))
            resp = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.AUTHENTICATION_FAILED,
                    'status': False}
            return make_response(jsonify(resp), resp['code'])
        except jwt.DecodeError as exp:
            applog.error("JWT VALIDATION INTERNAL | Invalid jwt token received :" + str(exp))
            resp = {'code': StatusCode.AUTHENTICATION_ERROR, 'data': {}, 'message': AppMessages.INVALID_JWT,
                    'status': False}
            return make_response(jsonify(resp), resp['code'])
        except Exception as exp:
            applog.error("JWT VALIDATION INTERNAL | Exception occured while authenticating :" + str(exp))
            resp = {'code': StatusCode.INTERNAL_SERVER_ERROR, 'data': {},
                    'message': AppMessages.TRY_AGAIN, 'status': False}
            return make_response(jsonify(resp), resp["code"])
        return func(*args, **kwargs)

    return decorated


def get_auth_id_from_token(auth_token):
    """
    this function returns the auth0_id from auth_token.
    :args auth_token
    :return: auth0_id
    """
    applog.info("GET AUTH ID FROM TOKEN | decoding auth id")
    token = auth_token.split("Bearer ")[-1]
    decode = jwt.decode(token,
                        options={"verify_signature": False, "verify_exp": True})
    auth0_id = decode["sub"].split("|")[-1]
    applog.info("GET AUTH ID FROM TOKEN | return the decoded auth id")
    return auth0_id


def credit_score_range_check(credit_score):
    """ This function checks the credit score and returns the score range,score_ranges_text
    Arg: credit_score
    """
    applog.info("CREDIT SCORE RANGE CHECK | Going to check score range and "
                     "returns score_ranges_text")
    score_ranges = None
    score_ranges_text = None
    if credit_score:
        if 300 <= credit_score <= 600:
            score_ranges = "300-600"
            score_ranges_text = "Very poor"
        elif 601 <= credit_score <= 657:
            score_ranges = "601-657"
            score_ranges_text = "Poor"
        elif 658 <= credit_score <= 719:
            score_ranges = "658-719"
            score_ranges_text = "Fair"
        elif 720 <= credit_score <= 780:
            score_ranges = "720-780"
            score_ranges_text = "Good"
        elif 781 <= credit_score <= 850:
            score_ranges = "781-850"
            score_ranges_text = "Excellent"
    else:
        score_ranges = "0-300"
        score_ranges_text = "Very poor"

    return score_ranges, score_ranges_text


def credit_score_factors():
    """
    This function returns static score factors
    """
    score_factors = [
        {
            "title": "Payment History",
            "description": "Pay ontime, every time, over and over again",
            "impact": "high impact"
        },
        {
            "title": "Credit Utilization",
            "description": "Use less than 30% of available credit to maximize score. Pay at least 70 % of "
                           "your limit each month",
            "impact": "high impact"
        },
        {
            "title": "Derogatory Marks",
            "description": "Anything that goes to a collections agency or public record is bad news",
            "impact": "high impact"
        },

        {
            "title": "Age of Credit",
            "description": "The longer you have credit, the better. Future you will thank you for paying "
                           "ontime now",
            "impact": "medium impact"
        },

        {
            "title": "Total Accounts",
            "description": "Use a variety of accounts responsibly",
            "impact": "low impact"
        },
        {
            "title": "Hard Inquiries",
            "description": "When you apply for credit, it shows on your report up to 2 years, "
                           "but their effects fade over time",
            "impact": "low impact"
        }
    ]

    return score_factors
