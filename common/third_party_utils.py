from datetime import datetime, timezone
import json
from log_data import ThirdPartyLoggerJson
from secret_manager import SecreteData
import requests
import os
from logging.config import dictConfig
from requests.structures import CaseInsensitiveDict
from logging import FileHandler, Formatter
from logger_utils import CustomFormatter
from aws_sns import SNSHelper
import logging

def third_party_log_config():
    key = SecreteData()
    # configuring third party log
    configPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    log_var = int(key.THIRD_PARTY_LOG_ENABLED)
    if log_var == 1:  # writing to console
        configFile = configPath + '/ThirdPartyLogConfig.json'
    elif log_var == 2:  # writing to file
        configFile = configPath + '/ThirdPartyLogConfig1.json'
    elif log_var == 3:  # both writing to file and console
        configFile = configPath + '/ThirdPartyLogConfig2.json'
    else:  # default writing to console
        configFile = configPath + '/ThirdPartyLogConfig1.json'
    with open(configFile, 'r') as logConfigFile:
        logConfig = json.load(logConfigFile)

    dictConfig(logConfig)

class ThirdPartyResponse(dict):
    '''
    This class is used for logging third party information in json format and also mask's the sensable information.
    '''
    mask_list = ["id","password","userId","firstName","lastName","email"]
    file_type = "json"

    def __init__(self, id=None, key=None, value=None, user_id=None, microservice=None, vendor=None, action=None,
    action_url=None, action_type=None, request_headers=None, request_payload=None,
    response_headers=None, response_payload=None, response_status_code=None ,timestamp = datetime.now(timezone.utc)):
        
        dict.__init__(self, id=id, key=key, value=value, user_id=user_id,
        microservice=microservice, vendor=vendor, action=action, action_url=action_url, action_type=action_type,
        request={"headers":self.get_copy(request_headers),"payload":self.get_copy(request_payload)},
        response={"headers":self.get_copy(response_headers),"StatusCode":response_status_code,"payload":self.get_copy(response_payload)},timestamp=timestamp)
        
        #getting sensible data list from SecreteData object and appending masking list to same variable
        self.keys = SecreteData()
        try:
            self.sensible_data = json.loads(self.keys.SENSIBLE_DATA)
        except:
            self.sensible_data = []
        self.sensible_data = self.sensible_data + self.mask_list
        
        # get logger
        self.logger = ThirdPartyLoggerJson.get_logger("info")
        
    def get_copy(self,dict_obj):
        #if content of variable is dictionary or list then it will return copy of it also it will check if content is json convertable then it will convert it to dictionary
        if isinstance(dict_obj,dict) or isinstance(dict_obj,list):
            new_obj = dict_obj.copy()
            return new_obj
        
        if isinstance(dict_obj,CaseInsensitiveDict):
            # checking if dictionary object is CaseInsensitiveDict type and converting it to dictionary and then will be used in masking
            try:
                return dict(dict_obj.copy())
            except:
                pass
        return dict_obj

    def set_response(self,id, key, value, user_id, microservice, vendor, action,
    action_url = None, action_type = None, request_headers = None, request_payload = None,
    response_headers = None, response_status_code=None , response_payload = None, timestamp = datetime.now(timezone.utc)):
        # this method is used for setting the dictionary values
        self['id'] = id
        self['key'] = key
        self['value'] = value
        self['user_id'] = user_id
        self['microservice'] = microservice
        self['vendor'] = vendor
        self['action'] = action
        self['action_url'] = action_url
        self['request'] = {"headers":self.get_copy(request_headers),"payload":self.get_copy(request_payload)}
        self['response'] = {"headers":self.get_copy(response_headers),"StatusCode": response_status_code,"payload":self.get_copy(response_payload)}
        self['action_type'] = action_type
        self['timestamp'] = timestamp

    def extract_from_request(self,request:requests.models.PreparedRequest):
        # this method is used for extracting information,
        # we can pass the response.request object which contains all the information about request
        try:
            payload = request.body
            if payload != None and "Content-Type" in request.headers and str(request.headers["Content-Type"]).lower() == "application/json":
                #copying dictionary to prevent changing of the object data
                payload = self.get_copy(json.loads(request.body))
        except:
            payload = ""

        self["action_type"] = request.method
        self["action_url"] = request.url
        self['request'] = {"headers":self.get_copy(request.headers),"payload":payload}
    
    def extract_from_response(self,response:requests.models.Response):
        # this method is used for extracting information,
        # we can pass the requests.models.Response object which contains all the information about response
        try:
            payload = (response.content)
            if payload != None and "Content-Type" in response.headers and str(response.headers["Content-Type"]).lower() == "application/json":
                #copying dictionary to prevent changing of the object data
                payload = self.get_copy(json.loads(response.content))
        except:
            payload = ""

        self["response"] = {"headers":self.get_copy(response.headers),"StatusCode":response.status_code,"payload":payload}

    def extract_from_request_response(self,response:requests.models.Response):
        #this method will extract information from request and response object
        self.extract_from_request(response.request)
        self.extract_from_response(response)

    def mask_nested_keys(self, data, keys_to_remove):
        # this function is recursively called for masking sensible information.
        if data != None and isinstance(data,dict):
            for key in keys_to_remove:
                if key in data:
                    rep_val = "XXXXXXXXX"
                    if key.lower().strip() == "email" and len(data[key].split("@")) > 1:
                        rep_val = rep_val +"@"+ data[key].split("@")[1]
                    data[key] = rep_val

            for value in data.values():
                if isinstance(value, dict):
                    self.mask_nested_keys(value, keys_to_remove)

                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) or isinstance(item, list):
                            self.mask_nested_keys(item, keys_to_remove)
    
    def get_file_name(self,table_name, primary_key):
        d_time = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M_%S_%f")
        return f"{table_name}_{primary_key}_T_{d_time}.{self.file_type}"

    def log_data(self,table_name,primary_key, db_name = None):
        # this method masks the request and response payload and then logges the information in json format 
        self.mask_nested_keys(self["request"],self.sensible_data)
        self.mask_nested_keys(self["response"],self.sensible_data)
        if self.keys.THIRD_PARTY_LOGGING_SERVICE == "event":
            # publish the log to aws sns
            sns_obj = SNSHelper(logging)
            if db_name == None:
                db_name = self.keys.CREDIT_LIMIT_DB_NAME

            msg = {
            "env": self.keys.REDIS_PREFIX.replace("_",""),
            "db_name": db_name,
            "file_name": self.get_file_name(table_name,primary_key),
            "data": dict(self),
            "table_name": table_name
            }
            Subjectname = self.keys.REDIS_PREFIX + db_name +"_"+ table_name
            code = sns_obj.sns_helper(self.keys.THIRD_PARTY_LOGGING_SNS_ARN, msg, Subjectname)
            self.logger.info(json.dumps(dict(self),default=str))
            
        else:
            # set name and create file
            self.set_file_name(table_name, primary_key)
            # log the information
            self.logger.info(json.dumps(dict(self),default=str))
            self.restore_defaults()
        return dict(self)

    def restore_defaults(self):
        # calls restore methods
        self.remove_handlers()
        self.restore_handlers()

    def set_file_name(self,table_name, primary_key):
        # this method is used for keeping information's about handlares and also changes name for the handler file
        self.handler_to_restore = []
        self.handler_to_remove = []
        self.format_changed_handlers = {}
        for hand in self.logger.handlers:
            if isinstance(hand,FileHandler):
                self.handler_to_restore.append(hand)
                self.logger.removeHandler(hand)
                new_hand = self.get_new_handler(hand.level,table_name, primary_key)
                self.logger.addHandler(new_hand)
                self.handler_to_remove.append(new_hand)
            else:
                if not isinstance(hand.formatter,CustomFormatter):
                    # Changing formatter for handler to track informations about the request
                    # assigning new formatter will not effect the handler because it uses its original formatter syntax
                    default_formatter = hand.formatter
                    self.format_changed_handlers[hand] = default_formatter
                    hand.setFormatter(CustomFormatter(default_formatter._fmt))
                
    def get_new_handler(self,level,table_name, primary_key):
        # this method will return new handler with new file and name
        hand = FileHandler(f"../logs/third_party/{self.get_file_name(table_name, primary_key)}","a")
        hand.setFormatter(Formatter("%(message)s"))
        hand.setLevel(level)
        return hand
    
    def reset_handler_formatter(self):
        # this method is used for setting original formatter to its handlers
        if self.format_changed_handlers:
            for hand, default_formatter in self.format_changed_handlers.items():
                hand.setFormatter(default_formatter)

    def remove_handlers(self):
        # it is used for removing handler from logger
        if len(self.handler_to_remove) > 0:
            for hand in self.handler_to_remove:
                self.logger.removeHandler(hand)

    def restore_handlers(self):
        # its used for restoring the handler to its default handler
        if len(self.handler_to_restore) > 0:
            for hand in self.handler_to_restore:
                self.logger.addHandler(hand)