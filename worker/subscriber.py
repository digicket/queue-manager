# Worker entrypoint

from functools import partial
from queue import Queue
import logging
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from worker.config import settings
from worker.message_processor import MessageProcessor
from worker.utils.task_scheduler import TaskScheduler

logger = logging.getLogger(__name__)


class Subscriber:
    def __init__(self):
        self._client = boto3.client('sqs', region_name=settings.QUEUE_REGION)
        self._scheduler = TaskScheduler()
        self._completed_queue = Queue()
        self._message_processor = MessageProcessor(self._completed_queue)

    def _listen_for_messages(self):
        """
        Start the message listener and schedule workers
        """
        # Number of messages to get = Number of free workers.
        free_worker_size = self._scheduler.get_free_worker_size()
        try:
            # Wait to receive.
            response = self._client.receive_message(
                QueueUrl=settings.QUEUE_URL,
                WaitTimeSeconds=settings.QUEUE_WAIT_TIME,
                MaxNumberOfMessages=free_worker_size,
            )
        except (ClientError, BotoCoreError) as ex:
            logger.critical('Failed to receive message. Error: {0}'.format(ex))
            time.sleep(10)  # sleep before retrying. Could be transient issue.
            return

        self._schedule_message_workers(response)

    def _schedule_message_workers(self, response):
        """
        Get the messages from response and start workers
        Args:
             response: Response from SQS queue long poll.
        """
        if 'Messages' not in response:
            logging.info('No messages in queue')
            return

        messages = response.get('Messages', [])
        logger.debug('{0} messages received from SQS queue'.format(len(messages)))

        for message in messages:
            self._scheduler.add_task_to_pool(
                partial(self._message_processor.process_message, message)
            )

    def _delete_handled_messages(self):
        """
        Delete any previously handled messages completed in threads
        """
        if self._completed_queue.empty():
            return

        # Delete completed messages from queue (from previous receive)
        # If no messages are present in SQS for a long time, these messages
        # will be in acked state till deleted.
        while not self._completed_queue.empty():
            message_handle = self._completed_queue.get()
            try:
                self._client.delete_message(
                    QueueUrl=settings.QUEUE_URL, ReceiptHandle=message_handle,
                )
            except (ClientError, BotoCoreError) as ex:
                logger.critical('Failed to delete message. Error: {0}'.format(ex))

    def start_subscription_workers(self):
        """
        Listen for messages in batches and process them in threads
        """
        while True:
            # Wait for a free worker thread
            if not self._scheduler.is_task_pool_vacant():
                continue

            # Audit and restart on failures
            try:
                self._delete_handled_messages()
            except Exception as ex:
                logger.critical('Failed to delete message. Error: {0}'.format(ex))

            try:
                self._listen_for_messages()
            except Exception as ex:
                logger.critical('Failed to retrieve or process messages. Error: {0}'.format(ex))

