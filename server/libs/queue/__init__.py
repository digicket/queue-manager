# Queue Interface

import abc
import enum

_queue_instances: tuple = ()


class QueueIface(metaclass=abc.ABCMeta):
    _instance = None

    def __new__(cls):
        """
        Singleton
        """
        if cls._instance is None:
            cls._instance = super(QueueIface, cls).__new__(cls)
        return cls._instance

    @abc.abstractmethod
    def type(self):
        pass

    @abc.abstractmethod
    def publish(self, message):
        """
        Publish a message to the queue
        Args:
            message(dict): Message to write. Will be converted to string
        Returns:
            str: ID of the message (from SQS)
        """
        pass


class QueueTypes(enum.Enum):
    SQS = 'SQS'


def get_queue(type: QueueTypes=QueueTypes.SQS) -> QueueIface:
    """
    Get the queue instance
    Args:
        type(QueueTypes): Type of queue
    Returns:
        QueueIface: Instance
    Raises:
        NotImplementedError: When invalid type is provided
    """
    global _queue_instances

    for inst in _queue_instances:
        if inst.type() == type:
            return inst

    instances = list()
    if type == QueueTypes.SQS:
        from server.libs.queue import SQS
        instances.append(SQS())
    else:
        raise NotImplementedError('Invalid Queue type')

    _queue_instances = (inst for inst in instances)
    for inst in _queue_instances:
        if inst.type() == type:
            return inst


