from status_codes import StatusCode
from secret_manager import SecreteData


class SetCode:
    def __init__(self, logger):
        if logger:
            self.logger = logger

    def code_check(self, status_code):
        sec_key = SecreteData()
        skip_code = sec_key.SKIP_CODES
        if status_code in skip_code:
            return status_code
        else:
            code = self.get_first_digit(status_code)
            if code == 2:
                return StatusCode.SUCCESS
            elif code == 4:
                return StatusCode.VALIDATION_ERROR
            else:
                return StatusCode.INTERNAL_SERVER_ERROR

    def get_first_digit(self, number):
        if number < 10:
            return number
        return self.get_first_digit(number // 10)
