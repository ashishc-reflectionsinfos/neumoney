import json
import traceback

from secret_manager import SecreteData


class LoggerResponse:
    def __init__(self, logger):
        if logger:
            self.logger = logger
        self.keys = SecreteData()

    def logger_response(self, data):
        """ This function is used to log the response data and to remove sensible data from the response
            Params:
                data
            Returns:
        """
        response = {}
        try:
            sensible_data = json.loads(self.keys.SENSIBLE_DATA)
            response = self.remove_nested_keys(data, sensible_data)
            if response:
                self.logger.info(f"LOGGER RESPONSE | Logging the response data :{response}")
            else:
                self.logger.info(f"LOGGER RESPONSE | Failed to log response data")

        except Exception as exc:
            self.logger.error(traceback.format_exc())
            raise f"LOGGER RESPONSE | Failed to log response data {exc}"

        finally:
            return response

    def remove_nested_keys(self, data, keys_to_remove):
        for key in keys_to_remove:
            if key in data:
                del data[key]

        for value in data.values():
            if isinstance(value, dict):
                self.remove_nested_keys(value, keys_to_remove)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) or isinstance(item, list):
                        self.remove_nested_keys(item, keys_to_remove)

        return data
