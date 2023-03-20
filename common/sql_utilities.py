import os

import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'common'))
from app_response import AppResponse
from utilities import Utils
from string_table import AppMessages


class SqlUtils:

    @staticmethod
    def response_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['feedback'] = AppResponse()
            app.config['terms_condition'] = AppResponse()
            app.config['privacy_policy'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config feedback, t&c, pp',
                app_response
            )

    # @staticmethod
    # def get_app_setting(logger, app, sql_handler_obj):
    #
    #     app_response = AppResponse()
    #     try:
    #         SqlUtils.response_config(logger, app)
    #         logger.info("Calling sqlHandler object, enter get customer feedback qst function")
    #         app_response = sql_handler_obj.get_app_settings(app)
    #         if app_response['code'] == 200:         # checking the response code
    #             logger.info("successfully returned feedback questions")
    #         else:
    #             logger.info("failed to return feedback questions")
    #         logger.info("Ended sqlHandler object, enter get customer feedback qst function")
    #     except Exception as excp:
    #         Utils.process_exception(
    #             excp,
    #             logger,
    #             f'{AppMessages.INTERNAL_ERROR} during fetching app settings',
    #             app_response
    #         )
    #     finally:
    #         logger.info("completed CustomerProfileMgr.get_customer_feedback_qst")
    #
    #     return app_response

    @staticmethod
    def resp_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['countries'] = AppResponse()
            app.config['states'] = AppResponse()
            app.config['occupation'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config countries, states and occupation',
                app_response
            )

    @staticmethod
    def get_settings(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.resp_config(logger, app)
            logger.info("Calling sqlHandler object, enter into functions function")
            resp_countries = sql_handler_obj.get_countries(app)
            resp_states = sql_handler_obj.get_states(app)
            resp_occupation = sql_handler_obj.get_occupation(app)

            if resp_countries['code'] == 200 & resp_states['code'] == 200 & resp_occupation['code'] == 200:
                # if resp_countries['code'] == 200 :
                logger.info("successfully returned countries")
            else:
                logger.info("failed to return countries")
            logger.info("Ended sqlHandler object, enter get countries function")
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching countries, states and occupation',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_countries")

        return app_response

    @staticmethod
    def citizen_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['citizenship_info'] = AppResponse()
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config citizenship',
                app_response
            )

    @staticmethod
    def enrollment_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['enrollment_info'] = AppResponse()
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config enrollment',
                app_response
            )

    @staticmethod
    def get_citizen_info(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.citizen_config(logger, app)
            logger.info("Calling sqlHandler object, enter get_citizen_info function")
            # app_response = sql_handler_obj.get_citizen_info(app)
            app_response = sql_handler_obj.citizenship_data(app)
            if app_response['code'] == 200:  # checking the response code
                logger.info("successfully got citizenship info")
            else:
                logger.info("failed to return citizenship info")
            logger.info("Ended sqlHandler object, enter get citizenship info  function")
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching customer citizenship',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_customer_feedback_qst")

        return app_response

    @staticmethod
    def get_enrollment_info(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.enrollment_config(logger, app)
            logger.info("Calling sqlHandler object, enter get_enrollment_info function")
            app_response = sql_handler_obj.enrollment_data(app)
            if app_response['code'] == 200:  # checking the response code
                logger.info("successfully got enrollment info")
            else:
                logger.info("failed to return citizenship info")
            logger.info("Ended sqlHandler object, enter get_enrollment_info  function")
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching enrollment info',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_enrollment_info")

        return app_response

    @staticmethod
    def education_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['education'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config education',
                app_response
            )

    @staticmethod
    def get_education(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.education_config(logger, app)
            logger.info("Calling sqlHandler object, enter get_education  function")
            app_response = sql_handler_obj.get_education(app)
            if app_response['code'] == 200:  # checking the response code
                logger.info("successfully returned education")
            else:
                logger.info("failed to return education")
            logger.info("Ended sqlHandler object, enter get education")

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during get education',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_education")

        return app_response

    @staticmethod
    def intimation_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['intimation'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config intimation',
                app_response
            )

    @staticmethod
    def get_intimation(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.intimation_config(logger, app)
            logger.info("Calling sqlHandler object, enter get intimation function")
            app_response = sql_handler_obj.get_intimation(app)
            if app_response['code'] == 200:  # checking the response code
                logger.info("successfully returned get_intimation")
            else:
                logger.info("failed to return intimation")
            logger.info("Ended sqlHandler object, enter get_intimation function")


        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching get_intimation',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_intimation")

        return app_response

    @staticmethod
    def verification_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['verification'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config verification',
                app_response
            )

    @staticmethod
    def get_verification(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.verification_config(logger, app)
            logger.info("Calling sqlHandler object, enter get_verification function")
            app_response = sql_handler_obj.get_verification(app)
            if app_response['code'] == 200:  # checking the response code
                logger.info("successfully returned get_verification")
            else:
                logger.info("failed to return get_verification")
            logger.info("Ended sqlHandler object, enter get_verification function")


        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching get_verification',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_verification")

        return app_response

    @staticmethod
    def emp_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['employment'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config employment',
                app_response
            )

    @staticmethod
    def get_employment_settings(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.emp_config(logger, app)
            logger.info("Calling sqlHandler object, enter into get employment function")
            resp_emp = sql_handler_obj.get_employment(app)

            if resp_emp['code'] == 200:
                logger.info("successfully returned employment list")
            else:
                logger.info("failed to return employment list")
            logger.info("Ended sqlHandler object, enter get employment settings function")
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching employment list',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_employment_list")

        return app_response

    @staticmethod
    def std_config(logger, app):
        app_response = AppResponse()

        try:
            app.config['student'] = AppResponse()

        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during setting app config student',
                app_response
            )

    @staticmethod
    def get_student_settings(logger, app, sql_handler_obj):

        app_response = AppResponse()
        try:
            SqlUtils.std_config(logger, app)
            logger.info("Calling sqlHandler object, enter into get student function")
            resp_std = sql_handler_obj.get_student(app)

            if resp_std['code'] == 200:
                logger.info("successfully returned student list")
            else:
                logger.info("failed to return student list")
            logger.info("Ended sqlHandler object, enter get student settings function")
        except Exception as excp:
            Utils.process_exception(
                excp,
                logger,
                f'{AppMessages.INTERNAL_ERROR} during fetching student list',
                app_response
            )
        finally:
            logger.info("completed CustomerProfileMgr.get_student_list")

        return app_response
