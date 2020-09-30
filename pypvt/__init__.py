import logging

from pypvt.element_fluid_description import ElementFluidDescription
from pypvt.field_fluid_description import FieldFluidDescription
from pypvt.bopvt import BoPVT


# A new handler to store "raw" LogRecords instances
class RecordsListHandler(logging.Handler):
    """
    A handler class which stores LogRecord entries in a list
    """

    def __init__(self, r_list):
        """
        Initiate the handler
        :param records_list: a list to store the LogRecords entries
        """
        self.records_list = r_list
        super().__init__()

    def emit(self, record):
        self.records_list.append(record)


records_list = []
_pvt_logger = logging.getLogger(__name__)
_pvt_logger.addHandler(RecordsListHandler(records_list))


# @property
def get_pvt_logger():
    return _pvt_logger


def get_pvt_records_list():
    return records_list
