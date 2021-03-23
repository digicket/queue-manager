# Message processor
import json
import logging


logger = logging.getLogger(__name__)


class MessageProcessor:
    _instance = None
    """Singleton Message Processor"""
    def __new__(cls, completed_queue):
        """
        Singleton
        """
        if cls._instance is None:
            cls._instance = super(MessageProcessor, cls).__new__(cls)
        cls._instance._completed_queue = completed_queue
        return cls._instance

    def __init__(self, completed_queue):
        """
        Initialize the message processor. Places message ReceiptHandle in completed_queue
        after the message is processed
        Args:
            completed_queue(Queue): for completed message ReceiptHandles
        """
        self._completed_queue = completed_queue

    def process_message(self, message):
        """
        Process the message and mark as completed
        Args:
            message:
        """
        try:
            msg_payload = json.loads(message['Body'])
            message_json = json.loads(msg_payload['Message'])
            # Process code here
            logger.info('Message: {0}'.format(message_json))
        except (KeyError, ValueError):
            logger.error('Failed to process message: {0}'.format(message))
        self._completed_queue.put(message['ReceiptHandle'])
