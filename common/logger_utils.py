import logging
from flask import request
from functools import wraps
import uuid
import re
import json
from secret_manager import SecreteData
import os
import jwt
from redis import Redis


def get_redis_cache(key, is_json=True):
    '''This function is a copy of get_redis_cache from redis_cache file, to avoide circular import'''
    sec_key = SecreteData()
    host = sec_key.REDIS_SERVER
    port = sec_key.REDIS_PORT
    prefix = sec_key.REDIS_PREFIX
    key = prefix + key
    success = True
    data = ''
    try:
        redis = Redis(host=host, decode_responses=True,port=port)
        if redis.ping():
            logging.info("Connected to Redis")
            if is_json:
                data = redis.get(key)
                if data:
                    data = json.loads(data)
            else:
                data = redis.get(key)
    except Exception:
        success = False
    finally:
        redis.close()
        return success, data

def get_user_uuid_from_token():
    '''This function is used for extracting user_uuid from token and cache it in the request-headers object
    for using it in all logs till request-response cycle'''
    try:
        token = request.headers["Authorization"]
        if "Bearer" not in token:
            raise Exception("Not an jwt token")
        raw_token = token.split(" ")[-1]
        response = jwt.decode(raw_token, options={"verify_signature": False, "verify_exp": True})
        auth_id = response['sub'].split('|')[1]
        status, user_uuid = get_redis_cache(auth_id, True)
        if status and user_uuid:
            return user_uuid
        else:
            return False
    except:
        return False

def get_user_uuid_from_args():
    '''This function is used for checking if user_uuid is present in request args and then it returns the value'''
    try:
        args = request.args
        if "user_uuid" in args:
            return args["user_uuid"]
        elif "uuid" in args:
            return args["uuid"]
        else:
            return False 
    except:
        return False

def get_user_uuid_from_body():
    '''This function is used for checking if user_uuid is present in request body and then it returns the value'''
    try:
        data=json.loads(request.data)
        if "user_uuid" in data:
            return data["user_uuid"]
        elif "uuid" in data:
            return data["uuid"]
        else:
            return False
    except:
        return False   

def search_user_uuid_in_request_object():
    '''This functions is used for getting user_uuid from either one of the function.'''
    token_user_uuid = get_user_uuid_from_token()
    if token_user_uuid:
        return token_user_uuid
    body_user_uuid = get_user_uuid_from_body()
    if body_user_uuid:
        return body_user_uuid
    args_user_uuid = get_user_uuid_from_args()
    if args_user_uuid:
        return args_user_uuid
    return False
    
def get_user_uuid():
    '''This function checks for attribute and sets value to the attribute x-User-UUID-Custom'''
    try:
        # check if request objects is initalized
        request.headers
        try:
            # check if the attribute is set, if its set then check if it is None or not and then send the response
            user_uuid = getattr(request.headers,"x-User-UUID-Custom")
            return user_uuid
        except:
            # get user_uuid from token
            user_uuid = search_user_uuid_in_request_object()
            if user_uuid:
                # set user_uuid to request headers objects so that we dont have to call get_user_uuid_from_token function again and again
                setattr(request.headers,"x-User-UUID-Custom",user_uuid)
                return user_uuid
            else:
                setattr(request.headers,"x-User-UUID-Custom",False)
                return False
    except:
        return False

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

def get_request_id():
    #getting value from the header for this function so the the value will change dynamically 
    try:
        #check headers for the id and if its not present then we have to create new one and then append to 
        return request.headers["x-amzn-RequestId"]
    except:
        try:
            # before creating new reqiest id, check if its already present if its present then create new one
            new_req_id = str(getattr(request.headers,"x-RequestId-custom"))
        except:
            new_req_id = str(uuid.uuid4())
            setattr(request.headers,"x-RequestId-custom",new_req_id)
        return new_req_id
    
def get_x_request_referral_Id():
    #getting value from the header for this function so the the value will change dynamically
    try:
        return request.headers["x-request-referral-Id"]
    except:
        return getattr(request.headers,"x-request-referral-Id")
        
def set_x_request_referral_Id(value):
    # this function is used for setting refral id to the headers
    setattr(request.headers,"x-request-referral-Id",str(value))
    return True

def check_for_headers_and_log():
    '''This function is used for providing field and value to be assigned to the logging'''
    log_field_value = {}
    try:
        #checking if headers is initalized or not if its not that means currently log is not being executed for request 
        request.headers
        log_field_value["req_id"] = get_request_id
    except:
        pass
    try:
        request.headers["x-request-referral-Id"]
        log_field_value["ref_id"] = get_x_request_referral_Id
    except:
        try:
            getattr(request.headers,"x-request-referral-Id")
            log_field_value["ref_id"] = get_x_request_referral_Id
        except:
            pass
        
    if get_user_uuid():
        log_field_value["user_uuid"] = get_user_uuid
    
    return log_field_value

class CustomFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super().__init__(fmt, datefmt, style, validate)

    def format(self,record):
        '''This is the main method which will change the logging data and append required data to the output'''
        actual_log = super().format(record)
        key_val = check_for_headers_and_log()
        actual_log = self.change_actual_string(actual_log,key_val)
        return actual_log
    
    def change_actual_string(self,actual_log:str,key_val:dict):
        '''This method is used to append values to the log'''
        split = re.split(" : ",actual_log)
        for key,fun_or_str in key_val.items():
            try:
                if callable(fun_or_str):
                    val = fun_or_str()
                else:
                    val = str(fun_or_str)
            
                #if val not in actual_log:
                split[0] = split[0] + f" [{key}-"+val+"]"
            except:
                pass
        return " : ".join(split)

def change_log_format_and_add_value(logger):
    '''This function is used for assigning Customeformatter to the log handler'''
    dict_of_handler_with_its_formatter = {}
    for hand in logger.handlers:
        actual_format = hand.formatter
        if not isinstance(actual_format,CustomFormatter):
            hand.setFormatter(CustomFormatter(actual_format._fmt))
            dict_of_handler_with_its_formatter[hand] = actual_format
    return dict_of_handler_with_its_formatter

# def reset_handlar(handler,actual_format):
#     '''This function is used for reseting format to previous format'''
#     if handler != None:
#         if isinstance(actual_format,CustomFormatter):
#             handler.setFormatter(actual_format)

def reset_list_of_handlers(dict_of_handler_with_its_formatter:dict):
    '''This function is used for reseting handlers with its orignal formatter'''
    for hand,default_formatter in dict_of_handler_with_its_formatter.items():
        hand.setFormatter(default_formatter)

#################### log function decorator ################################## 
def log_decorator(logger_name):
    # this decorator is used for assigning fields dynamically to the current logger with logger_name
    # outher function is used for collecting parameter and the inner function is actually decorator
    def outer_decor_to_support_retrive_logger_name(func):
        @wraps(func)
        def log_wrapper(*args,**kwargs):
            logger = logging.getLogger(logger_name)
            dict_of_handler_with_its_formatter = change_log_format_and_add_value(logger)
            resp = func(*args,**kwargs)
            reset_list_of_handlers(dict_of_handler_with_its_formatter)
            return resp
        return log_wrapper
    return outer_decor_to_support_retrive_logger_name


###################### log decorator for single api ########################
def log_api_decorator(func):
    '''This function is used for decorating api for setting logger format for each logger and reseting it to its actual formatter'''
    @wraps(func)
    def log_wrapper(*args,**kwargs):
        dict_of_handler_with_its_formatter = get_all_logger_handlers_and_add_custom_formatter()
        resp = func(*args,**kwargs)
        reset_list_of_handlers(dict_of_handler_with_its_formatter)
        return resp
    return log_wrapper

def get_all_logger_handlers_and_add_custom_formatter():
    '''This function is used for assigning CustomFormatter to each logger handlers for changing value dynamically'''
    path = get_log_config_path()
    dict_of_handler_with_its_formatter = {}
    with open(path,"r") as f:
        all_loger_info = json.loads(f.read())
        for loger_name,val in all_loger_info["loggers"].items():
            logger = logging.getLogger(loger_name)
            for hand in logger.handlers:
                actual_format = hand.formatter
                if not isinstance(actual_format,CustomFormatter):
                    # storing info for resetting it formatter later
                    dict_of_handler_with_its_formatter[hand] = actual_format
                    hand.setFormatter(CustomFormatter(actual_format._fmt))
    return dict_of_handler_with_its_formatter