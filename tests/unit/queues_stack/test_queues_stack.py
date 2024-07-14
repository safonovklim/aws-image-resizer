import unittest
import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.queues_stack.main import QueuesStack


class TestMyCdkStack(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = QueuesStack(self.app, "queues-stack", source_bucket_arn="arn:aws:s3:::source_bucket_arn")

    def test_queue_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.resource_count_is("AWS::SQS::Queue", 1)
        template.has_resource_properties("AWS::SQS::Queue", {})

    # TODO: add tests for s3 notification

    def test_output_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.has_output("ResizingQueueArn", {
            "Export": {
                "Name": "ResizingQueueArn"
            },
        })
