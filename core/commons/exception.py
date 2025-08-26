import logging
import traceback

logger_error = logging.getLogger(__name__)


class CustomException(Exception):

    def __init__(self, status: int = 500,
                 message: str = 'Le service est momentanément indisponible. Veuillez reessayez plutard...'):
        self.status = status
        self.detail = message
        logger_error.exception(self.detail)
        traceback.print_stack()
