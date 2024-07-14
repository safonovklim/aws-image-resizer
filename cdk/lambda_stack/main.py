from aws_cdk import Stack, CfnOutput
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_lambda_event_sources as lambda_sources
import aws_cdk.aws_iam as iam
import aws_cdk.aws_sqs as sqs
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, id: str, source_bucket_arn: str, destination_bucket_arn: str, source_queue_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. Create IAM role that will be used during lambda runtime
        # must allow reading from source bucket, writing to destination + logs
        # Refer to https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
        execution_role = iam.Role(self, "ResizerLambdaRole",
                                  assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                                  managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
                                ])
        # 1.1 - Allow reading from Source bucket
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[source_bucket_arn + "/*"]
            )
        )
        # 1.2 - Allow writing to Destination bucket
        execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[destination_bucket_arn + "/*"]
            )
        )

        # 2. Create lambda function
        function = lambda_.Function(self, "ResizerFunction",
                                    runtime=lambda_.Runtime.PYTHON_3_12,
                                    handler="main.handler",
                                    code=lambda_.Code.from_asset("./lambda"),
                                    role=execution_role)

        # 3. Attach Lambda to SQS source
        source_queue = sqs.Queue.from_queue_arn(self, id="SourceQueue", queue_arn=source_queue_arn)
        invoke_event_source = lambda_sources.SqsEventSource(source_queue)
        function.add_event_source(invoke_event_source)

        # 4. Export Function ARNs for further reference
        CfnOutput(self, "ResizerFunctionArn", value=function.function_arn)
