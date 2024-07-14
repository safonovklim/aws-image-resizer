from constructs import Construct
from aws_cdk import Stack, Fn
from cdk.queues_stack.main import QueuesStack
from cdk.lambda_stack.main import LambdaStack
from cdk.buckets_stack.main import BucketsStack

class AwsImageAutoresizerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Import S3 bucket and outputs
        self.buckets_stack = BucketsStack(self, "BucketsStack")
        source_bucket_arn = Fn.import_value("SourceBucketArn")
        destination_bucket_arn = Fn.import_value("DestinationBucketArn")

        # 2. Import SQS queue and outputs
        self.queues_stack = QueuesStack(self, "QueuesStack", source_bucket_arn=source_bucket_arn)
        resizing_queue_arn = Fn.import_value("ResizingQueueArn")

        # 3. Import Lambda Stack
        self.lambda_stack = LambdaStack(self, "LambdaStack",
                                        source_bucket_arn=source_bucket_arn,
                                        destination_bucket_arn=destination_bucket_arn,
                                        source_queue_arn=resizing_queue_arn
                                        )

