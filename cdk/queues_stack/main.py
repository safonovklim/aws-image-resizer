from constructs import Construct
from aws_cdk import Stack, CfnOutput
import aws_cdk.aws_sqs as sqs
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_notifications as s3_notifications


class QueuesStack(Stack):

    def __init__(self, scope: Construct, id: str, source_bucket_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. Create the queue
        queue = sqs.Queue(self, "ResizingQueue")

        # 2. Subscribe queue to s3 bucket notifications
        source_bucket = s3.Bucket.from_bucket_arn(self, "SourceBucket", bucket_arn=source_bucket_arn)
        source_bucket.add_event_notification(s3.EventType.OBJECT_CREATED,
                                             s3_notifications.SqsDestination(queue))

        # 3. Export Queue ARNs for further reference
        CfnOutput(self, "ResizingQueueArn", value=queue.queue_arn, export_name="ResizingQueueArn")
