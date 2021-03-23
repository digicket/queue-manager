import unittest
from functools import partial
from unittest import mock

from botocore.exceptions import BotoCoreError, ClientError

from server.errors import QueueError
from server import consts
from server.libs.queue.sqs import SQS


class TestSQS(unittest.TestCase):
    def test_singleton(self):
        s1 = SQS()
        s2 = SQS()

        self.assertEqual(s1, s2)

    def test_publish(self):
        s = SQS()
        test_message = {'foo': 'bar'}
        test_id = 'foo_id'
        s._client = mock.Mock()
        ret = {consts.SQS_MESSAGE_ID_KEY: test_id}
        s._client.send_message = mock.Mock(return_value=ret)
        resp = s.publish(test_message)

        self.assertEqual(resp, test_id)

    def test_publish_failed(self):
        s = SQS()
        test_message = {'foo': 'bar'}
        s._client = mock.Mock()
        s._client.send_message = mock.Mock()
        s._client.send_message.side_effect = BotoCoreError()

        self.assertRaises(QueueError, partial(s.publish, test_message))

        s._client.delete_message.side_effect = ClientError({}, 'bar')
        self.assertRaises(QueueError, partial(s.publish, test_message))