# Entrypoint

from logging.config import fileConfig
import logging
import sys

import uvicorn

from server.config import settings
from worker.subscriber import Subscriber

fileConfig('logging_config.ini')
logger = logging.getLogger(__name__)


def start_server():
    """Start Web app server"""
    uvicorn.run('server.api:app', host=settings.HOST, port=settings.PORT)


def start_worker():
    """Start message processor worker"""
    Subscriber().start_subscription_workers()


if __name__ == '__main__':
    if sys.argv[1] == 'server':
        start_server()
    elif sys.argv[1] == 'worker':
        start_worker()
    else:
        raise ValueError('Invalid start command')
