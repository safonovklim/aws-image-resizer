import unittest
import aws_cdk as core
import aws_cdk.assertions as assertions
import app_config
from unittest.mock import patch

from cdk.lambda_stack.main import LambdaStack

class TestLambdaStack(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = LambdaStack(self.app, "LambdaStack",
                                 source_bucket_arn="arn:aws:s3:::source_bucket_arn",
                                 destination_bucket_arn="arn:aws:s3:::destination_bucket_arn",
                                 source_queue_arn="arn:aws:sqs:us-east-1:123456789012:source_queue_arn")

    def test_iam_role_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.resource_count_is("AWS::IAM::Role", 1)
        template.has_resource_properties("AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        }
                    }
                ],
                "Version": "2012-10-17"
            }
        })

    def test_lambda_function_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.resource_count_is("AWS::Lambda::Function", 1)
        template.has_resource_properties("AWS::Lambda::Function", {
            "Handler": "main.handler",
            "Runtime": "python3.12",
            "Timeout": 15,
            "Environment": {
                "Variables": {
                    "DESTINATION_BUCKET_ARN": "arn:aws:s3:::destination_bucket_arn",
                    "RESIZE_HEIGHT": str(app_config.resize_height),
                    "RESIZE_WIDTH": str(app_config.resize_width),
                }
            }
        })

    @patch('aws_cdk.aws_lambda_event_sources.SqsEventSource.__init__', return_value=None)
    def test_sqs_event_source_added(self, mock_sqs_event_source):
        template = assertions.Template.from_stack(self.stack)
        template.resource_count_is("AWS::Lambda::EventSourceMapping", 1)

    def test_output_created(self):
        template = assertions.Template.from_stack(self.stack)
        template.has_output("ResizerFunctionArn", {})
