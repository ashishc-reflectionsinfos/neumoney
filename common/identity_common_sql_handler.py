import datetime

from sqlalchemy.orm import Session

from app_response import AppResponse
from utilities import Utils


class IdentitySQLFunctionProvider:

    def __new__(cls, *args):
        if cls is IdentitySQLFunctionProvider:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def register_user(self, data):
        """

        This function is used to the user and adding the values to mst_user_login
        :param data: request data
        :return: App response
        """

        try:
            self.logger.info("Start Registration")
            self.session = Session(self.connection)
            mst_user_details = self.base_auto_map.classes.mst_user_details
            self.logger.info("Query for similar phone number in the database started")
            mst_user_login_mob = self.session.query(mst_user_details) \
                .filter(mst_user_details.mobile_number == int(data['phone_no'])).first()
            self.logger.info("Query for similar phone number in the database executed successfully")
            # self.logger.info("Query for similar email id in the database executed")
            # mst_user_login_email = self.session.query(mst_user_details) \
            #     .filter(mst_user_details.email_id == data['email']).first()
            # self.logger.info("Query for similar email id in the database executed successfully")
            # current_time = datetime.datetime.now()

            if mst_user_login_mob:
                self.app_response["code"] = 500
                self.app_response["message"] = "Phone number is already register with different email"
                self.app_response["status"] = False
                self.logger.info("User already exist")
            else:
                res_data = {}
                # updating the mst_user_details table
                self.logger.info("Executing Query for updating otp data")
                self.session.add(mst_user_details(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email_id=data['email'],
                    created_date=datetime.datetime.now(),
                    mobile_number=data['phone_no'],
                    auth0_id=data['Auth0_id']
                ))

                res_data['phone_number'] = data['phone_no']
                self.app_response["code"] = 200
                self.app_response["message"] = "User Registered successfully"
                self.app_response['data'] = res_data
                self.app_response["status"] = True
                self.logger.info("User added")

                self.session.commit()
                self.logger.info("Query for inserting user registration data executed")

            self.session.close()

        except Exception as exp:
            Utils.process_exception(exp, self.logger, 'Exception occurred while registering',
                                    self.app_response)
        finally:
            self.logger.info("Ending registration user details")
            if self.session is not None:
                self.session.close()
            return self.app_response

    def get_phone(self, data):
        resp_dic = {}
        self.app_response = AppResponse(500, resp_dic, "Unable to process request", False)
        try:
            self.logger.info("Starting function  do_login ")
            self.session = Session(self.connection)
            if "email" in data:
                email = data['email']
                self.session = Session(self.connection)
                mst_user = self.base_auto_map.classes.mst_user_details
                mst_otp = self.base_auto_map.classes.mst_otp
                user = self.session.query(mst_user) \
                    .filter(mst_user.email_id == email).first()
                if user:
                    resp_dic['phone_number'] = user.mobile_number
                    resp_dic['phone_verified'] = user.phone_verified
                    resp_dic["auth0_id"] = user.auth0_id
                    otp_data = self.session.query(mst_otp) \
                        .filter(mst_otp.mobile_number == str(user.mobile_number)).first()
                    if not otp_data:
                        self.logger.info("Executing Query for inserting otp data")
                        self.session.add(mst_otp(
                            otp_time=datetime.datetime.now(),
                            mobile_number=resp_dic["phone_number"]
                        ))
                        self.session.commit()
                    self.app_response['data'] = resp_dic
                    self.app_response['message'] = "Phone number retrieved"
                    self.app_response["code"] = 200
                    self.app_response["status"] = True
            self.logger.info("Ending function getPhone")
        except Exception as excp:
            Utils.process_exception(excp, self.logger,
                                    "Exception occurred CustomerLoginSQLHandlerProvider.do_login()",
                                    self.app_response)

        finally:
            if self.session is not None:
                self.session.close()
            return self.app_response

    def do_login(self, data):
        resp_dic = {}
        self.app_response = AppResponse(500, resp_dic, "Unable to process request", False)
        try:
            self.logger.info("Starting function  do_login ")
            self.session = Session(self.connection)
            if "email" in data:
                user_detail = {}
                mst_user_details = self.base_auto_map.classes.mst_user_details
                mst_otp = self.base_auto_map.classes.mst_otp

                user_data = self.session.query(mst_user_details) \
                    .filter(mst_user_details.email_id == data['email']) \
                    .first()

                if user_data:
                    otp_data = self.session.query(mst_otp) \
                        .filter(mst_otp.mobile_number == str(user_data.mobile_number)) \
                        .first()
                    if otp_data:
                        otp_data.oob_code_auth0 = data['oob_code']
                        user_data.access_token = data['access_token']
                        user_data.refresh_token = data['refresh_token']
                        email = data['email']
                        user_detail['first_name'] = user_data.first_name
                        user_detail['last_name'] = user_data.last_name
                        user_detail['email'] = email
                        user_detail['phone_no'] = user_data.mobile_number
                        user_detail['do_not_disturb'] = True
                        user_detail['is_phone_verified'] = data['phone_verified'] if data['phone_verified'] else False
                        resp_dic["user_detail"] = user_detail
                        resp_dic["access_token"] = data["access_token"]
                        resp_dic["refresh_token"] = data["refresh_token"]
                        self.session.commit()
                        self.app_response['data'] = resp_dic
                        self.app_response['message'] = "Login_successfully"
                        self.app_response["code"] = 200
                        self.app_response["status"] = True
            self.logger.info("Ending function  do_login ")
        except Exception as excp:
            Utils.process_exception(excp, self.logger,
                                    "Exception occurred CustomerLoginSQLHandlerProvider.do_login()",
                                    self.app_response)
        finally:
            if self.session is not None:
                self.session.close()
            return self.app_response

    def save_user_data(self, data):
        resp_dic = {}
        user_detail = {}
        self.app_response = AppResponse(500, {}, "Unable to process request", False)
        try:
            self.logger.info("Starting function save_user_data")
            self.session = Session(self.connection)
            mst_user_details = self.base_auto_map.classes.mst_user_details
            if "email" in data:
                email = data['email']
                user_data = self.session.query(mst_user_details) \
                    .filter(mst_user_details.email_id == data['email']) \
                    .first()
                if user_data:
                    if "access_token" in data:
                        user_data.access_token = data["access_token"]
                        resp_dic["access_token"] = data["access_token"]
                    if "refresh_token" in data:
                        user_data.refresh_token = data["refresh_token"]
                        resp_dic["refresh_token"] = data["refresh_token"]
                        user_detail['first_name'] = user_data.first_name
                        user_detail['last_name'] = user_data.last_name
                        user_detail['email'] = email
                        user_detail['phone_no'] = user_data.mobile_number
                        user_detail['do_not_disturb'] = True
                        user_detail['is_phone_verified'] = data['phone_verified'] if data['phone_verified'] else False
                        resp_dic["user_detail"] = user_detail
                        resp_dic["access_token"] = data["access_token"]
                        resp_dic["refresh_token"] = data["refresh_token"]
                    self.session.commit()
                    self.app_response.set_response(200, resp_dic, "User data updated ", True)
            self.session.close()
        except Exception as excp:
            Utils.process_exception(excp, self.logger,
                                    "Exception occurred CustomerLoginSQLHandlerProvider.do_login()",
                                    self.app_response)
        finally:
            if self.session is not None:
                self.session.close()
            return self.app_response
