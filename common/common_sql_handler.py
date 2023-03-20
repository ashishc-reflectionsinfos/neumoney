import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'common'))
from app_response import AppResponse
from utilities import Utils
from string_table import AppMessages


class CommonSQLHandlerProvider:
    def __init__(self, logger):
        if logger:
            self.logger = logger

        self.sqlHandlerObj = None

    def __enter__(self):
        class SqlQueryHandler:
            def __init__(self, logger):
                if logger:
                    self.logger = logger

                sql_client_driver = os.getenv("dbDriver")
                connection_string = sql_client_driver \
                                    + os.getenv("dbUser") \
                                    + ":" + os.getenv("dbPass") \
                                    + "@" + os.getenv("dbHost") \
                                    + "/" + os.getenv("dbName")
                self.stri = connection_string

                self.session = None
                self.connection = None
                self.engine = None
                self.engine = create_engine(connection_string,
                                            connect_args={'options': '-csearch_path={}'.format("onboarding")})

                self.connection = self.engine.connect()
                self.base_auto_map = automap_base()
                self.base_auto_map.prepare(self.engine, reflect=True)

                self.app_response = AppResponse()

            '''
            def get_feedback_settings(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database mst_app_settings")
                    self.session = Session(self.connection)  # connecting to the database
                    mst_app_settings = self.base_auto_map.classes.mst_app_settings
                    self.logger.info("query to retrieve all feedback questions from the table")
                    result = self.session \
                        .query(mst_app_settings) \
                        .filter(mst_app_settings.name == 'feedback_questions') \
                        .all()
                    self.logger.info("Fetched all feedback values from mst_app_settings table")
                    if result:

                        resp_dic = self.get_feedback(app, result)
                        if resp_dic['code'] == 200:
                            resp.set_response(200, {}, "successfully retrieved feedback questions", True)
                            self.logger.info("successfully retrieved feedback questions")
                        else:
                            resp.set_response(500, {}, "failed to get feedback questions", False)
                            self.logger.info("Failed to retrieved feedback questions")

                    else:
                        self.logger.info("No data found in mst_app_settings")
                        resp.set_response(404, {}, "Not data found in DB", False)
                    self.session.close()
                    self.logger.info("successfully ending function get feedback settings")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during fetching feedback questions', resp)
                finally:
                    return resp

            def get_terms_condition_and_privacy_settings(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database mst_app_settings")
                    self.session = Session(self.connection)  # connecting to the database
                    mst_app_settings = self.base_auto_map.classes.mst_app_settings
                    self.logger.info("query to retrieve all terms conditions and privacy policy from the table")
                    result = self.session \
                        .query(mst_app_settings) \
                        .filter(or_(mst_app_settings.name == 'terms_conditions', mst_app_settings.name == 'privacy_policy')) \
                        .all()
                    self.logger.info("Fetched all terms conditions and privacy policy from mst_app_settings table")
                    if result:
                        self.logger.info("going to config terms condition and privacy policy")
                        resp_dic_t = self.get_terms_condition(app, result)
                        resp_dic_p = self.get_privacy_policy(app, result)
                        if resp_dic_t['code'] == 200 & resp_dic_p['code'] == 200:
                            resp.set_response(200, {}, "successfully retrieved terms condition and privacy policy", True)
                            self.logger.info("successfully retrieved terms condition and privacy policy")
                        else:
                            resp.set_response(500, {}, "failed to get terms conditions and privacy policy", False)
                            self.logger.info("Failed to retrieved terms condition and privacy")

                    else:
                        self.logger.info("No data found in mst_app_settings")
                        resp.set_response(404, {}, "Not data found in DB", False)
                    self.session.close()
                    self.logger.info("successfully ending function get_terms_and_condition_settings")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during fetching terms conditions', resp)
                finally:
                    return resp

            def get_app_settings(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database mst_app_settings")
                    self.session = Session(self.connection)  # connecting to the database
                    mst_app_settings = self.base_auto_map.classes.mst_app_settings
                    self.logger.info("query to retrieve all data from the table")
                    result = self.session \
                        .query(mst_app_settings) \
                        .all()
                    self.logger.info("Fetched all values from mst_app_settings table")
                    if result:

                        feedback = self.get_feedback(app, result)
                        if feedback['code'] == 200:
                            self.logger.info("successfully returned feedback questions")
                        else:
                            self.logger.info("failed to return feedback questions")
                        terms_conditions = self.get_terms_condition(app, result)
                        if terms_conditions['code'] == 200:
                            self.logger.info("successfully returned terms and conditions")
                        else:
                            self.logger.info("failed to return terms and conditions")
                        privacy_policy = self.get_privacy_policy(app, result)
                        if privacy_policy['code'] == 200:
                            self.logger.info("successfully returned privacy policy")
                        else:
                            self.logger.info("failed to return privacy policy")
                        resp.set_response(200, {}, "successfully retrieved data from DB table", True)
                        self.logger.info("successfully retrieved data from mst_app_settings table")
                    else:
                        self.logger.info("No data found in mst_app_settings")
                        resp.set_response(404, {}, "Not data found in DB", False)
                    self.session.close()
                    self.logger.info("successfully ending function get app settings")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during get_app_settings', resp)
                finally:
                    return resp

            def get_feedback(self, app, result):
                resp = AppResponse()
                try:
                    self.logger.info("going to get value for feedback_questions from mst_app_settings table")

                    app.config['feedback'] = self.get_settings_value('feedback_questions', result)
                    if app.config['feedback']['code'] == 200:
                        resp.set_response(200, {}, "successfully retrieved feedback questions", True)
                        self.logger.info("successfully retrieved feedback questions")
                    else:
                        resp.set_response(500, {}, "failed to get feedback questions", False)
                        self.logger.info("Failed to retrieved feedback questions")
                    self.logger.info("ending function get_settings_value")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during fetching feedback questions', resp)
                finally:
                    return resp

            def get_terms_condition(self, app, result):
                resp = AppResponse()
                try:
                    self.logger.info("going to get value for terms and condition from mst_app_settings table")

                    app.config['terms_condition'] = self.get_settings_value('terms_conditions', result)
                    if app.config['terms_condition']['code'] == 200:
                        resp.set_response(200, {}, "successfully retrieved terms and condition", True)
                        self.logger.info("successfully retrieved terms and condition")
                    else:
                        resp.set_response(500, {}, "failed to get terms and condition", False)
                        self.logger.info("Failed to retrieved terms and condition")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during fetching terms and condition',
                                            resp)
                finally:
                    return resp

            def get_privacy_policy(self, app, result):
                resp = AppResponse()
                try:
                    self.logger.info("going to get value for privacy policy from mst_app_settings table")

                    app.config['privacy_policy'] = self.get_settings_value('privacy_policy', result)
                    if app.config['privacy_policy']['code'] == 200:
                        resp.set_response(200, {}, "successfully retrieved privacy_policy", True)
                        self.logger.info("successfully retrieved privacy policy")
                    else:
                        resp.set_response(500, {}, "failed to get privacy policy", False)
                        self.logger.info("Failed to retrieved privacy policy")
                    self.logger.info("ending function get_settings_value")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during fetching privacy and policy',
                                            resp)
                finally:
                    return resp

            def get_settings_value(self, name, result):
                resp = AppResponse()
                try:
                    self.logger.info(f"going to get value for {name} from mst_app_settings table")

                    for i in result:
                        if i.name == name:
                            if name == 'feedback_questions':
                                data = json.loads(i.value)
                            else:
                                data = i.value
                            resp.set_response(200, data, f"successfully retrieved {name} details", "True")

                        else:
                            self.logger.info(f"{name} value not found in table")

                    self.logger.info(f"successfully retrieved {name} value")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during fetching feedback ,T&C, PP',
                                            resp)
                finally:
                    return resp

            def get_intro_reels(self):
                """ Gets Intro info media reels.
                    Args:
                        headers: auth token
                    Returns:
                        Response JSON with media reels:
                                              intro_id:
                                            media_link:
                """
                resp = AppResponse()
                try:
                    self.logger.info("Getting Intro info media reels")
                    self.session = Session(self.connection)

                    mst_app_setting = self.base_auto_map.classes.mst_app_settings   # connecting to the database
                    self.logger.info("Getting all intro info media links")

                    self.logger.info("Executing Query for getting Intro reels media link")
                    item = self.session \
                        .query(mst_app_setting) \
                        .filter(or_(mst_app_setting.name == "media_1", mst_app_setting.name == "media_2",
                                    mst_app_setting.name == "media_3", mst_app_setting.name == "media_4",)) .all()
                    data = []
                    if item:
                        for i in item:             # iterating through items,
                            # to collect the data and store in an object
                            obj = {"intro_id": i.row_id, "media_link": i.value}
                            data.append(obj)
                        self.logger.info("got all intro info media links data")
                        resp.set_response(200, data, "successfully obtained all media links", True)
                    else:
                        self.logger.info("No media links data available in database")
                        resp.set_response(404, {}, "Not data found in DB", False)

                    self.logger.info("Query for getting into media reels Executed")
                    self.session.commit()
                    self.session.close()
                    self.logger.info("Successfully Retrieved intro info media reels")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during retrieving intro info reels', resp)
                finally:
                    self.logger.info("Ending get intro info reels")
                    if self.session is not None:
                        self.session.close()
                    return resp
            '''

            def citizenship_data(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database cst_citizenship_lookup")
                    self.session = Session(self.connection)  # connecting to the database
                    cst_citizenship_lookup = self.base_auto_map.classes.mst_citizenship
                    self.logger.info("query to retrieve all citizenship info data")
                    result = self.session \
                        .query(cst_citizenship_lookup) \
                        .all()
                    self.logger.info("Fetched citizenship info data")
                    if result:
                        self.logger.info("going to config citizenship data")
                        citizeninfo = self.get_citizen_data(result)
                        if citizeninfo['code'] == 200:
                            app.config['citizenship_info'] = citizeninfo
                            resp.set_response(200, {}, "successfully retrieved  citizenship info data", True)
                            self.logger.info("successfully retrieved citizenship info data")
                        else:
                            resp.set_response(500, {}, "failed to get citizenship info data", False)
                            self.logger.info("Failed to retrieve citizenship info data")

                    else:
                        self.logger.info("No data found in cst_citizenship_lookup")
                        resp.set_response(404, {}, "Not data found in DB", False)
                    self.session.close()
                    self.logger.info("successfully ending function citizenship_info")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during fetching citizenship info data',
                                            resp)
                finally:
                    return resp

            def get_citizen_data(self, result):
                '''
                  code to get data from cst_citizenship_lookup table in customer schema

                '''
                resp = AppResponse()
                # citizen_data={}
                citizen_data = []
                try:
                    self.logger.info(f"going to get value for from cst_citizenship_lookup")
                    if result:
                        for item in result:
                            types = {}
                            types["code"] = item.id
                            types["Description"] = item.name
                            citizen_data.append(types)
                        resp.set_response(200, citizen_data, "successfully got citizenship info", True)
                    else:
                        self.logger.info(f" failed to retrieve data from cst_citizenship_lookup ")
                        resp.set_response(500, {}, "Failed to get citizenship info", False)
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during citizen ship info data',
                                            resp)
                finally:
                    return resp

            def enrollment_data(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database cst_enrollment_lookup")
                    self.session = Session(self.connection)  # connecting to the database
                    cst_enrollment_lookup = self.base_auto_map.classes.mst_school_type
                    self.logger.info("query to retrieve all enrollment info ")
                    result = self.session \
                        .query(cst_enrollment_lookup) \
                        .all()
                    self.logger.info("Fetched enrollment info data")
                    if result:
                        self.logger.info("going to config enrollment data")
                        enrollmentinfo = self.get_enrollment_data(result)
                        if enrollmentinfo['code'] == 200:
                            app.config['enrollment_info'] = enrollmentinfo
                            resp.set_response(200, {}, "successfully retrieved  enrollment info ", True)
                            self.logger.info("successfully retrieved enrollment info ")
                        else:
                            resp.set_response(500, {}, "failed to get enrollment info", False)
                            self.logger.info("Failed to retrieve enrollment info ")

                    else:
                        self.logger.info("No data found in cst_enrollment_lookup")
                        resp.set_response(404, {}, "Not data found in DB", False)
                    self.session.close()
                    self.logger.info("successfully ending function enrollment_data")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during fetching Enrollment data',
                                            resp)
                finally:
                    return resp

            def get_enrollment_data(self, result):
                '''
                  code to get data from cst_enrollment_lookup table in customer schema

                '''
                resp = AppResponse()
                enrollment_data = []
                try:
                    self.logger.info(f"going to get value for from cst_enrollment_lookup")
                    if result:
                        for item in result:
                            types = {}
                            types["code"] = item.id
                            types["Description"] = item.name
                            enrollment_data.append(types)
                        resp.set_response(200, enrollment_data, "successfully got enrollment info", True)
                    else:
                        self.logger.info(f" failed to retrieve data from cst_enrollment_lookup ")
                        resp.set_response(500, {}, "filed to get enrollment info", False)
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during retrieving enrollment info data',
                                            resp)
                finally:
                    return resp

            def get_countries(self, app):
                """ this function is used to retrieve all countries and corresponding code

                input:

                reponse:
                                    {
                        "code": 200,
                        "data": [
                            "Afghanistan",
                            "AF",
                            "Albania",
                            "AL",
                            "Algeria",
                            "DZ"
                        ],
                        "detail": {},
                        "message": "successfully got all countries",
                        "status": "Success"
                    }

                """
                resp = AppResponse()
                try:

                    self.logger.info("Going to function countries list, Getting all countries")
                    app.config['countries'] = self.countries_list()  # Function for fetching countries from DB

                    if app.config['countries']['code'] == 200:
                        self.logger.info("got all countries from database")
                        resp.set_response(200, {}, "successfully got all countries", True)
                    else:
                        self.logger.info("No countries data available in database")
                        resp.set_response(500, {}, "No data found in DB to get", False)

                    self.logger.info("successfully ending function get countries")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during list all countries', resp)
                finally:
                    return resp

            def countries_list(self):
                """ This function helps get the countries with code as response from database

                input:  engine : An "engine" is a Python object representing a database.

                reponse:
                 We get the countries with country code as response from database .

                        all_countries= [
                            "Afghanistan",
                            "AF",
                            "Albania",
                            "AL",
                            "Algeria",
                            "DZ"
                        ]

                """
                resp = AppResponse()
                try:
                    self.logger.info("connecting to database")
                    self.session = Session(self.connection)
                    countries = self.base_auto_map.classes.mst_country
                    self.logger.info("Getting all states by executing query")
                    country_result = self.session \
                        .query(countries) \
                        .all()
                    countries_list = []
                    if country_result:
                        for item in country_result:
                            obj = {"id": item.id, "name": item.name, "code": item.code}
                            countries_list.append(obj)

                        resp.set_response(200, countries_list, "successfully retrieved countries", True)
                    else:
                        self.logger.info("Countries not found in the table")
                        resp.set_response(500, {}, "failed to retrieved countries from DB", False)
                    self.session.close()
                    self.logger.info("ending function countries list")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during list all countries', resp)
                finally:
                    return resp

            def get_states(self, app):
                """
                Making connection with database and getting the list of states,
                Returns: Response (code, data, message, status)
                data: list of all states

                """
                resp = AppResponse()
                try:

                    self.logger.info("Going to function states list, Getting all states")
                    app.config['states'] = self.states_list()  # Function for fetching countries from DB

                    if app.config['states']['code'] == 200:
                        self.logger.info("got all states from database")
                        resp.set_response(200, {}, "successfully got all states", True)
                    else:
                        self.logger.info("No states data available in database")
                        resp.set_response(500, {}, "No states data in DB to get", False)

                    self.logger.info("successfully ending function get states")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during listing states', resp)
                finally:
                    return resp

            def states_list(self):

                resp = AppResponse()
                try:
                    self.logger.info("Going to connect with database")
                    self.session = Session(self.connection)
                    query_item = self.base_auto_map.classes.mst_state_code
                    self.logger.info("Getting all states by executing query")
                    states_result = self.session \
                        .query(query_item) \
                        .all()
                    all_states = []
                    if states_result:
                        for item in states_result:
                            obj = {"name": item.name, "code": item.state_code, "id": item.id}
                            all_states.append(obj)

                        self.logger.info("got all states and sending data as a response")
                        resp.set_response(200, all_states, "successfully retrieved all states", True)
                    else:
                        self.logger.info("No states data available in database")
                        resp.set_response(500, {}, "No states data found in DB to get", False)
                    self.session.close()
                    self.logger.info("ending function state list")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during listing states', resp)
                finally:
                    self.logger.info("Getting all states method completed")
                    return resp

            def get_occupation(self, app):
                """ Gets customer occupation.
                Args:
                    param:
                    headers:
                Returns:
                    Response JSON with customer occupation
                """
                resp = AppResponse()
                try:
                    self.logger.info("Going to function occupation list")
                    app.config['occupation'] = self.occupation_list()
                    if app.config['occupation']['code'] == 200:
                        self.logger.info("got all occupation from database")
                        resp.set_response(200, {}, "successfully got all occupation", True)
                    else:
                        self.logger.info("No occupation data available in database")
                        resp.set_response(500, {}, "No occupation data to get", False)
                    self.logger.info("successfully ending function get occupation")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} while getting all occupation list', resp)
                finally:
                    return resp

            def occupation_list(self):

                """ This function helps get the occupations  as response from database
                    input:  engine : An "engine" is a Python object representing a database.
                    reponse:
                     We get the occupations  as response from database .
                            "code": 200,
                            "data": [
                                "Accountants and auditors",
                                "Actors",
                                "Actuaries",
                                "Adhesive bonding machine operators and tenders",
                                "Administrative services managers",
                                "Advertising and promotions managers",
                                "Advertising sales agents"
                                ],
                            "message": "successfully got all occupation",
                            "status": "Success"
                    """
                resp = AppResponse()
                try:
                    self.logger.info("Going to connect with database")
                    self.session = Session(self.connection)
                    occupations = self.base_auto_map.classes.mst_occupation
                    self.logger.info("Getting all occupation by executing query")
                    get_occupation = self.session \
                        .query(occupations) \
                        .all()
                    all_occupations = []
                    if get_occupation:
                        for item in get_occupation:
                            obj = {"name": item.name, "code": item.id}
                            all_occupations.append(obj)

                        self.logger.info("got all occupation and sending data as a response")
                        resp.set_response(200, all_occupations, "successfully got all occupation", True)
                    else:
                        self.logger.info("No occupation data available in database")
                        resp.set_response(500, {}, "No occupation data to get", False)
                    self.session.close()
                    self.logger.info("ending function occupation list")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} during getting all occupations', resp)
                finally:
                    return resp

            def get_education(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database cst_unemployed_lookup")
                    self.session = Session(self.connection)  # connecting to the database
                    app.config['education'] = self.education_list()
                    if app.config['education']['code'] == 200:
                        self.logger.info("got all education_list from database")
                        resp.set_response(200, {}, "successfully got unemployed_list", True)
                    else:
                        self.logger.info("No unemployed list data available in database")
                        resp.set_response(500, {}, "No data found in DB to get", False)
                    self.session.close()
                    self.logger.info("successfully ending function get unemployed")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during getting education list', resp)
                finally:
                    return resp

            def education_list(self):
                """
                Making connection with database and getting the unemployment list,
                Returns: Response (code, data, message, status)
                data: id,code,description

                """
                resp = AppResponse()
                try:
                    cst_education = self.base_auto_map.classes.mst_education
                    self.logger.info("Getting education list by executing query")
                    get_education = self.session \
                        .query(cst_education) \
                        .all()
                    all_education = []
                    if get_education:
                        for item in get_education:
                            obj = {"description": item.name, "code": item.id}
                            all_education.append(obj)

                        self.session.commit()
                        self.session.close()
                        resp.set_response(200, all_education, "successfully got education list", True)
                    else:
                        self.logger.info("No education list available ")
                        resp.set_response(500, {}, "No education list available in DB", False)

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} while getting education list',
                                            resp)
                finally:
                    self.logger.info("Getting all education list function completed")
                return resp

            def get_intimation(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database cst_intimation_type_lookup")
                    self.session = Session(self.connection)  # connecting to the database
                    app.config['intimation'] = self.intimation_list()
                    if app.config['intimation']['code'] == 200:
                        self.logger.info("got all intimation list from database")
                        resp.set_response(200, {}, "successfully got intimation_list", True)
                    else:
                        self.logger.info("No intimation data available in database")
                        resp.set_response(500, {}, "No intimation data", False)
                    self.session.close()
                    self.logger.info("successfully ending function get_intimation")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during getting intimation list', resp)
                finally:
                    return resp

            def intimation_list(self):
                """
                Making connection with database and getting the intimation_list,
                Returns: Response (code, data, message, status)
                data: id,code,description

                """
                resp = AppResponse()
                try:
                    cst_intimation_type = self.base_auto_map.classes.cst_intimation_type_lookup
                    self.logger.info("Getting intimation_list by executing query")
                    get_intimation_type = self.session \
                        .query(cst_intimation_type) \
                        .all()
                    all_intimation_type = []
                    if get_intimation_type:
                        for item in get_intimation_type:
                            obj = {"description": item.description, "code": item.code}
                            all_intimation_type.append(obj)

                        self.session.commit()
                        self.session.close()
                        resp.set_response(200, all_intimation_type, "successfully got intimation_list", True)
                    else:
                        self.logger.info("No intimation_list available ")
                        resp.set_response(500, {}, "No intimation_list available", False)

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} while getting intimation_list',
                                            resp)
                finally:
                    self.logger.info("Getting all intimation_list function completed")
                    return resp

            def get_verification(self, app):
                resp = AppResponse()
                try:

                    self.logger.info("connecting to database cst_verification_type_lookup")
                    self.session = Session(self.connection)  # connecting to the database
                    app.config['verification'] = self.verification_list()
                    if app.config['verification']['code'] == 200:
                        self.logger.info("got all verification_list from database")
                        resp.set_response(200, {}, "successfully got verification_list", True)
                    else:
                        self.logger.info("No verification_list data available in database")
                        resp.set_response(500, {}, "No verification list data to get", False)
                    self.session.close()
                    self.logger.info("successfully ending function get verification_list")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during getting verification_list', resp)
                finally:
                    return resp

            def verification_list(self):
                """
                Making connection with database and getting the unemployment list,
                Returns: Response (code, data, message, status)
                data: id,code,description

                """
                resp = AppResponse()
                try:
                    cst_verification_type = self.base_auto_map.classes.cst_verification_type_lookup
                    self.logger.info("Getting verification list by executing query")
                    get_verification_type = self.session \
                        .query(cst_verification_type) \
                        .all()
                    all_verification_type = []
                    if get_verification_type:
                        for item in get_verification_type:
                            obj = {"description": item.description, "code": item.code}
                            all_verification_type.append(obj)

                        self.session.commit()
                        self.session.close()
                        resp.set_response(200, all_verification_type, "successfully got verification list", True)
                    else:
                        self.logger.info("No verification list available ")
                        resp.set_response(500, {}, "No verification list available", False)

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during getting verification list',
                                            resp)
                finally:
                    self.logger.info("Getting all verification list function completed")
                    return resp

            def get_employment(self, app):
                """
                Making connection with database and getting the list of employment,
                Returns: Response (code, data, message, status)
                data: list of all employment

                """
                resp = AppResponse()
                try:

                    self.logger.info("Going to function employment list, Getting all employment")
                    app.config['employment'] = self.employment_list()  # Function for fetching countries from DB

                    if app.config['employment']['code'] == 200:
                        self.logger.info("got all employment list from database")
                        resp.set_response(200, {}, "successfully got all employment list", True)
                    else:
                        self.logger.info("No employment list data available in database")
                        resp.set_response(500, {}, "No employment list data to get", False)

                    self.logger.info("successfully ending function get employment")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during getting all employment list', resp)
                finally:
                    return resp

            def employment_list(self):

                resp = AppResponse()
                try:
                    self.logger.info("Going to connect with database")
                    self.session = Session(self.connection)
                    query_item = self.base_auto_map.classes.mst_employment
                    self.logger.info("Getting all employment list by executing query")
                    employment_result = self.session \
                        .query(query_item) \
                        .all()
                    all_employment = []
                    if employment_result:
                        for item in employment_result:
                            obj = {"name": item.name, "code": item.id}
                            all_employment.append(obj)

                        self.logger.info("got all employment list and sending data as a response")
                        resp.set_response(200, all_employment, "successfully retrieved all employment list", True)
                    else:
                        self.logger.info("No employment list data available in database")
                        resp.set_response(500, {}, "No employment list data to get", False)
                    self.session.close()
                    self.logger.info("ending function employment list")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} while getting employment list', resp)
                finally:
                    self.logger.info("Getting all employment list method completed")
                    return resp

            def get_student(self, app):
                """
                Making connection with database and getting the list of student,
                Returns: Response (code, data, message, status)
                data: list of all student

                """
                resp = AppResponse()
                try:

                    self.logger.info("Going to function employment list, Getting all student")
                    app.config['student'] = self.student_list()  # Function for fetching countries from DB

                    if app.config['student']['code'] == 200:
                        self.logger.info("got all student list from database")
                        resp.set_response(200, {}, "successfully got all student list", True)
                    else:
                        self.logger.info("No student list data available in database")
                        resp.set_response(500, {}, "No student list data to get", False)

                    self.logger.info("successfully ending function get student")
                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR}during getting all student list', resp)
                finally:
                    return resp

            def student_list(self):

                resp = AppResponse()
                try:
                    self.logger.info("Going to connect with database")
                    self.session = Session(self.connection)
                    query_item = self.base_auto_map.classes.mst_student_info
                    self.logger.info("Getting all student list by executing query")
                    student_result = self.session \
                        .query(query_item) \
                        .all()
                    all_student = []
                    if student_result:
                        for item in student_result:
                            obj = {"name": item.name, "code": item.id}
                            all_student.append(obj)

                        self.logger.info("got all student list and sending data as a response")
                        resp.set_response(200, sorted(all_student, key=lambda x: x["code"]),
                                          "successfully retrieved all student list", True)
                    else:
                        self.logger.info("No student list data available in database")
                        resp.set_response(500, {}, "No student list data to get", False)
                    self.session.close()
                    self.logger.info("ending function student list")

                except Exception as excp:
                    Utils.process_exception(excp, self.logger,
                                            f'{AppMessages.INTERNAL_ERROR} while getting student list', resp)
                finally:
                    self.logger.info("Getting all student list method completed")
                    return resp

            def cleanup(self):
                self.logger.info("Going to do DB cleanup")
                try:
                    if self.session is not None:
                        self.session.close()
                    if self.connection is not None:
                        self.connection.close()
                    if self.engine is not None:
                        self.engine.dispose()
                except Exception as exp:
                    Utils.process_exception(exp, self.logger, 'Exception occurred during get_app_settings_chat',
                                            self.app_response)

        if self.sqlHandlerObj is None:
            self.logger.info("Going to initiate sqlHandler")
            self.sqlHandlerObj = SqlQueryHandler(self.logger)

        return self.sqlHandlerObj

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sqlHandlerObj.cleanup()
