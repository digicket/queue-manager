# SQS Queue

import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from server import consts
from server.config import settings
from server.errors import QueueError
from server.libs.queue import QueueIface, QueueTypes

logger = logging.getLogger(__name__)


class SQS(QueueIface):
    def __init__(self, **kwargs):
        self._client = boto3.client('sqs', region_name=settings.QUEUE_REGION)
        self._queue_url = settings.QUEUE_URL

    def type(self) -> QueueTypes:
        return QueueTypes.SQS

    def publish(self, message: dict) -> str:
        """
        Publish a message to the queue
        Args:
            message(dict): Message to write. Will be converted to string
        Returns:
            str: ID of the message (from SQS)
        """
        try:
            response = self._client.send_message(
                QueueUrl=self._queue_url,
                MessageBody=json.dumps(message)
            )
            return response[consts.SQS_MESSAGE_ID_KEY]
        except (ClientError, BotoCoreError) as ex:
            logger.error('Failed to send message. Error: {0}'.format(ex))

        raise QueueError('Failed to write to queue')
