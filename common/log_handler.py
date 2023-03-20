import logging
import sys


class AppLogHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(stream=sys.stdout)
        logging.Handler.__init__(self)

    # def emit(self, record) -> None:
    # rec = self.format(record) + '\r\n'
