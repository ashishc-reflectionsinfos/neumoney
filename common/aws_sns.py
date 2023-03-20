import json
import os

import boto3
from status_codes import StatusCode
from flask import current_app as cp

class SNSHelper:
    def __init__(self, logger):
        if logger:
            self.logger = logger

    @staticmethod
    def get_sns_client(logger):
        session = boto3.session.Session()
        sns_client = None
        logger.info("SNS HELPER | Going to get sns client connection")
        try:
            if "sns_client" in cp.config and cp.config['sns_client'] is not None:
                logger.info("SNS HELPER | Retriving sns client connection from cache.")
                sns_client = cp.config['sns_client']

            else:
                logger.info("SNS HELPER | Failed to fetch sns client from cache, creating new connection")
                if os.getenv("environment") == "local":
                    sns_client = session.client('sns',
                                            region_name=os.getenv("aws_secrete_manager_region"),
                                            aws_access_key_id=os.getenv("aws_access_key"),
                                            aws_secret_access_key=os.getenv("aws_secret_access_key"))
                else:
                    sns_client = session.client('sns',
                                                region_name=os.getenv("aws_secrete_manager_region"))
                cp.config['sns_client'] = sns_client
            
            logger.info("SNS HELPER | Successfully fetched sns connection")
        
        except Exception as exc:
            raise f"Failed to establish connection to sns, error message: {exc}"
        
        finally:
            logger.info("SNS HELPER | completed sns helper function")
            return sns_client
        
    def sns_helper(self, topic, publish, subject):
        """ This function is used to publish message using aws simple notification service
            Params:
                topic: ARN of sns
                publish
                subject
            Returns:
        """
        response_code = StatusCode.INTERNAL_SERVER_ERROR
        try:
            sns_client = self.get_sns_client(self.logger)
            response = sns_client.publish(TopicArn=topic, Message=json.dumps(publish, default=str),
                                          Subject=subject
                                          )
            if response['ResponseMetadata']['HTTPStatusCode'] == StatusCode.SUCCESS:
                response_code = StatusCode.SUCCESS
                self.logger.info(
                    "SNS HELPER | Successfully published notification through sns_helper function with status code 200")
            else:
                self.logger.info(
                    f"SNS HELPER | Failed to publish notification through sns_helper function, response:{response}")

        except Exception as exc:
            raise f"Failed to publish notification through sns {exc}"

        finally:
            self.logger.info("SNS HELPER | completed sns helper function")
            return response_code
