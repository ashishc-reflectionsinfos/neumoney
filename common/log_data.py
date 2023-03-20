import logging
from logger_utils import log_decorator

class ApplicationLogger:
    @log_decorator(logger_name = "info_application")
    def info(msg):
        return logging.getLogger('info_application').info(msg)

    @log_decorator(logger_name = "error_application")
    def error(msg):
        return logging.getLogger('error_application').error(msg)

    @log_decorator(logger_name = "debug_application")
    def debug(msg):
        return logging.getLogger('debug_application').debug(msg)

    @log_decorator(logger_name = "warning_application")
    def warn(msg):
        return logging.getLogger('warning_application').warn(msg)


class ThirdPartyLogger:
    @log_decorator(logger_name = "info_third_party")
    def info(msg):
        return logging.getLogger('info_third_party').info(msg)

    @log_decorator(logger_name = "error_third_party")
    def error(msg):
        return logging.getLogger('error_third_party').error(msg)

    @log_decorator(logger_name = "debug_third_party")
    def debug(msg):
        return logging.getLogger('debug_third_party').debug(msg)

    @log_decorator(logger_name = "warning_third_party")
    def warn(msg):
        return logging.getLogger('warning_third_party').warn(msg)

class ThirdPartyLoggerJson:
    @log_decorator(logger_name = "info_third_party_json")
    def info(msg):
        return logging.getLogger('info_third_party_json').info(msg)

    @log_decorator(logger_name = "error_third_party_json")
    def error(msg):
        return logging.getLogger('error_third_party_json').error(msg)

    @log_decorator(logger_name = "debug_third_party_json")
    def debug(msg):
        return logging.getLogger('debug_third_party_json').debug(msg)

    @log_decorator(logger_name = "warning_third_party_json")
    def warn(msg):
        return logging.getLogger('warning_third_party_json').warn(msg)

    def get_logger(l_type="debug"):
        l_type = l_type.lower()
        if l_type=="debug":
            return logging.getLogger('debug_third_party_json')
        elif l_type == "info":
            return logging.getLogger('info_third_party_json')
        elif l_type == "error":
            return logging.getLogger('error_third_party_json')
        elif l_type == "warn":
            return logging.getLogger('warning_third_party_json')
        else:
            return logging.getLogger('info_third_party_json')

class AuditLogger:
    @log_decorator(logger_name = "info_audit")
    def info(msg):
        return logging.getLogger('info_audit').info(msg)

    @log_decorator(logger_name = "error_audit")
    def error(msg):
        return logging.getLogger('error_audit').error(msg)

    @log_decorator(logger_name = "debug_audit")
    def debug(msg):
        return logging.getLogger('debug_audit').debug(msg)

    @log_decorator(logger_name = "warning_audit")
    def warn(msg):
        return logging.getLogger('warning_audit').warn(msg)
