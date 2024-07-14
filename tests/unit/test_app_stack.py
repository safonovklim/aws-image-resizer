import unittest
import aws_cdk as core
from cdk.lambda_stack.main import LambdaStack
from cdk.buckets_stack.main import BucketsStack
from cdk.queues_stack.main import QueuesStack

from cdk.app_stack import AwsImageAutoresizerStack


class TestAppStack(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = AwsImageAutoresizerStack(self.app, "app-stack")

    def test_imports(self):
        assert isinstance(self.stack.buckets_stack, BucketsStack)
        assert isinstance(self.stack.queues_stack, QueuesStack)
        assert isinstance(self.stack.lambda_stack, LambdaStack)
