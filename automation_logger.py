import sys
import logging
from logging.config import dictConfig

logging_config = dict(
    version=1,
    formatters={
        'verbose': {
            'format': ("[%(asctime)s] %(levelname)s "
                       "[%(name)s:%(lineno)s] %(message)s"),
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    handlers={
        'automation-process-logger': {'class': 'logging.handlers.RotatingFileHandler',
                             'formatter': 'verbose',
                             'level': logging.DEBUG,
                             'filename': 'logs/automation.log',
                             'maxBytes': 52428800,
                             'backupCount': 7},
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
    },
    loggers={
        'quiet_batch_process_logger': {
            'handlers': ['automation-process-logger'],
            'level': logging.DEBUG
        }
    }
)

dictConfig(logging_config)

quiet_batch_process_logger = logging.getLogger('quiet_batch_process_logger')

