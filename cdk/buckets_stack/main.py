from aws_cdk import Stack, CfnOutput
import aws_cdk.aws_s3 as s3
from constructs import Construct

class BucketsStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. Define Buckets
        s3_source = s3.Bucket(self, "Source")
        s3_dest = s3.Bucket(self, "Destination")

        # 2. Export Bucket ARNs for further reference
        CfnOutput(self, "SourceBucketArn", value=s3_source.bucket_arn, export_name="SourceBucketArn")
        CfnOutput(self, "DestinationBucketArn", value=s3_dest.bucket_arn, export_name="DestinationBucketArn")
