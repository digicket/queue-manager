import unittest
from unittest import mock

from botocore.exceptions import BotoCoreError, ClientError

from worker.config import settings
from worker.subscriber import Subscriber


class SubsciberTest(unittest.TestCase):
    def test__delete_handled_messages_empty(self):
        s = Subscriber()
        s._client = mock.Mock('mock_client')
        s._client.delete_message = mock.Mock('mock_delete_message')

        s._delete_handled_messages()
        s._client.delete_message.assert_not_called()

    def test__delete_handled_messages_contains(self):
        s = Subscriber()
        message_handle_list = ['foo', 'bar']
        for m_handle in message_handle_list:
            s._completed_queue.put(m_handle)
        s._client = mock.Mock('mock_client')
        s._client.delete_message = mock.Mock('mock_delete_message')

        s._delete_handled_messages()
        mock_calls = []
        for m_handle in message_handle_list:
            mock_calls.append(mock.call(QueueUrl=settings.QUEUE_URL, ReceiptHandle=m_handle))
        s._client.delete_message.assert_has_calls(mock_calls)

    def test__delete_handled_messages_failed(self):
        s = Subscriber()
        message_handle_list = ['foo', 'bar']
        for m_handle in message_handle_list:
            s._completed_queue.put(m_handle)
        s._client = mock.Mock('mock_client')
        s._client.delete_message = mock.Mock('mock_delete_message')
        s._client.delete_message.side_effect = ClientError({}, 'bar')

        s._delete_handled_messages()
        mock_calls = []
        for m_handle in message_handle_list:
            mock_calls.append(mock.call(QueueUrl=settings.QUEUE_URL, ReceiptHandle=m_handle))
        s._client.delete_message.assert_has_calls(mock_calls)

        s._client.delete_message.side_effect = BotoCoreError()

        s._delete_handled_messages()
        mock_calls = []
        for m_handle in message_handle_list:
            mock_calls.append(mock.call(QueueUrl=settings.QUEUE_URL, ReceiptHandle=m_handle))
        s._client.delete_message.assert_has_calls(mock_calls)

    def test__schedule_message_workers(self):
        s = Subscriber()
        response = {'Messages': ['foo']}
        s._scheduler.add_task_to_pool = mock.Mock('add_task_to_pool')

        s._schedule_message_workers(response)
        s._scheduler.add_task_to_pool.assert_called_once()

    def test__schedule_message_workers_no_messages(self):
        s = Subscriber()
        response = {'fizz': ['foo']}
        s._scheduler.add_task_to_pool = mock.Mock('add_task_to_pool')

        s._schedule_message_workers(response)
        s._scheduler.add_task_to_pool.assert_not_called()

        response = {'Messages': []}
        s._scheduler.add_task_to_pool = mock.Mock('add_task_to_pool')

        s._schedule_message_workers(response)
        s._scheduler.add_task_to_pool.assert_not_called()

    def test__listen_for_messages(self):
        s = Subscriber()
        ret = mock.Mock('mock_ret')
        message_count = 10
        s._scheduler.get_free_worker_size = mock.Mock(return_value=message_count)
        s._client = mock.Mock('mock_client')
        s._client.receive_message = mock.Mock('mock_receive_message', return_value=ret)
        s._schedule_message_workers = mock.Mock('mock__schedule_message_workers')

        s._listen_for_messages()
        s._schedule_message_workers.assert_called_with(ret)
        s._client.receive_message.assert_called_once_with(
                QueueUrl=settings.QUEUE_URL,
                WaitTimeSeconds=settings.QUEUE_WAIT_TIME,
                MaxNumberOfMessages=message_count,
            )

    @mock.patch('worker.subscriber.time')
    def test__listen_for_messages_fails(self, mock_time):
        mock_time.sleep = mock.Mock()
        s = Subscriber()
        message_count = 10
        s._scheduler.get_free_worker_size = mock.Mock(return_value=message_count)
        s._client = mock.Mock('mock_client')
        s._client.receive_message = mock.Mock('mock_receive_message')
        s._client.receive_message.side_effect = BotoCoreError()
        s._schedule_message_workers = mock.Mock('mock__schedule_message_workers')

        s._listen_for_messages()
        s._schedule_message_workers.assert_not_called()
        s._client.receive_message.assert_called_once_with(
            QueueUrl=settings.QUEUE_URL,
            WaitTimeSeconds=settings.QUEUE_WAIT_TIME,
            MaxNumberOfMessages=message_count,
        )
        mock_time.sleep.assert_called_once_with(10)
