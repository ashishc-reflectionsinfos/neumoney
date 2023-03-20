from flask import current_app as cp
from sqlalchemy import create_engine

from app_response import AppResponse
from log_data import ApplicationLogger as applog
from secret_manager import SecreteData
from string_table import AppMessages
from utilities import Utils
from sqlalchemy.orm import Session

class SqlBase:
    '''This class is used as a base class for all sql classes, this should be the super class for all sql codes.'''

    def __init__(self, logger=None, db_driver=None, db_user=None, db_pass=None, db_host=None, db_name=None,
                 schema=None, pool_size=None) -> None:
        '''This constructor takes optional values for the parameters and then connects to database and stores the
        session into class property '''

        if logger:
            self.logger = logger
        else:
            self.logger = applog

        key = SecreteData()
        if db_driver is None:
            db_driver = key.DB_DRIVER
        if db_user is None:
            db_user = key.DB_USER
        if db_pass is None:
            db_pass = key.DB_PASS
        if db_host is None:
            db_host = key.DB_HOST
        if db_name is None:
            db_name = key.CREDIT_LIMIT_DB_NAME
        if schema is None:
            schema = key.CREDIT_LIMIT_SCHEMA
        if pool_size is None:
            pool_size = key.POOL_SIZE

        sql_client_driver = db_driver
        connection_string = sql_client_driver \
                            + db_user \
                            + ":" + db_pass \
                            + "@" + db_host \
                            + "/" + db_name
        self.session = None
        self.connection = None
        self.engine = None
        self.logger.info("BASE SQL |Making database connection")
        if "engine" in cp.config and cp.config['engine'] is not None:
            self.logger.info("BASE SQL |Getting database connection from flask cache")
            self.engine = cp.config['engine']
        else:
            self.logger.info("BASE SQL |Creating new database connection and storing to flask cache")
            self.engine = create_engine(connection_string, pool_size=int(pool_size),
                                        connect_args={
                                            'options': '-csearch_path={}'.format(schema)})
            cp.config["engine"] = self.engine

        self.logger.info("BASE SQL |Successfully made connection to database")
        self.connection = self.engine.connect()
        self.app_response = AppResponse()
        self.session = Session(self.connection)
    def cleanup(self):
        self.logger.info("BASE SQL |Going to do DB cleanup")
        try:
            if self.session is not None:
                self.session.close()
            if self.connection is not None:
                self.connection.close()
        except Exception as exp:
            Utils.process_exception(exp, self.logger, AppMessages.SOMETHING_WENT_WRONG,
                                    self.app_response)
