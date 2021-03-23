# Message API
import logging
from typing import Any

from fastapi import APIRouter, status, HTTPException

from server.libs.queue import get_queue
from server.api.schemas.message import Message, ReturnMessage
from server.errors import QueueError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    '/message',
    description='Post a message to the queue',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ReturnMessage,
    tags=['message'],
)
def add_message(message_request: Message) -> Any:
    """
    Add the message to the queue
    Args:
        message_request:
    Returns:
        ReturnMessage: Response to the client
    Raises:
        HTTPException: On failure
    """
    try:
        return ReturnMessage(message_id=get_queue().publish(message_request.dict()))
    except QueueError as ex:
        logger.error('Failed to publish message: {0}'.format(ex))
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
