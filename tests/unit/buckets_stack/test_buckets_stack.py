import unittest
import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.buckets_stack.main import BucketsStack

class TestBucketsStack(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = BucketsStack(self.app, "BucketsStack")

    def test_buckets_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.resource_count_is("AWS::S3::Bucket", 2)

    def test_source_bucket_output_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.has_output("SourceBucketArn", {
            "Export": {
                "Name": "SourceBucketArn"
            },
        })

    def test_destination_bucket_output_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.has_output("DestinationBucketArn", {
            "Export": {
                "Name": "DestinationBucketArn"
            },
        })
