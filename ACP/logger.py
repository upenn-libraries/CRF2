import logging

from logging import FileHandler
from logging import Formatter


"""
format for 
1. Canvas errors
2. CRF errors
3. email errors

"""


LOG_FORMAT = (
    "%(asctime)s \t [%(levelname)s]: \t %(message)s \t in %(pathname)s:%(lineno)d"
)
LOG_LEVEL = logging.INFO


# canvas logger
CANVAS_LOG_FILE = "ACP/logs/canvas.log"

canvas_logger = logging.getLogger("Canvas")
canvas_logger.setLevel(LOG_LEVEL)
canvas_logger_file_handler = FileHandler(CANVAS_LOG_FILE)
canvas_logger_file_handler.setLevel(LOG_LEVEL)
canvas_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
canvas_logger.addHandler(canvas_logger_file_handler)

# crf logger

CRF_LOG_FILE = "ACP/logs/crf.log"

crf_logger = logging.getLogger("CRF")
crf_logger.setLevel(LOG_LEVEL)
crf_file_handler = FileHandler(CRF_LOG_FILE)
crf_file_handler.setLevel(LOG_LEVEL)
crf_file_handler.setFormatter(Formatter(LOG_FORMAT))
crf_logger.addHandler(crf_file_handler)

# email logger
EMAIL_LOG_FILE = "ACP/logs/email.log"

email_logger = logging.getLogger("email")
email_logger.setLevel(LOG_LEVEL)
email_file_handler = FileHandler(EMAIL_LOG_FILE)
email_file_handler.setLevel(LOG_LEVEL)
email_file_handler.setFormatter(Formatter(LOG_FORMAT))
email_logger.addHandler(email_file_handler)
