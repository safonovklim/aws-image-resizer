from constructs import Construct
from aws_cdk import Stack, CfnOutput, Duration
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_lambda_event_sources as lambda_sources
import aws_cdk.aws_iam as iam
import aws_cdk.aws_sqs as sqs
import app_config

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

        # 2. Import Pillow (image processing lib) as Lambda Layer)
        # PS: For simplicity of this task/solution, I used public dependency, but
        #     I highly recommend to pack and store dependencies yourself
        #     to ensure the best security and compatibility
        pillow_layer = lambda_.LayerVersion.from_layer_version_arn(self, "PillowLayer", layer_version_arn="arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-Pillow:2")

        # 2. Create lambda function
        # Pillow (image processing lib) attached as Lambda Layer
        # Source: https://github.com/keithrozario/Klayers/tree/master/deployments/python3.12
        function = lambda_.Function(self, "ResizerFunction",
                                    runtime=lambda_.Runtime.PYTHON_3_12,
                                    handler="main.handler",
                                    code=lambda_.Code.from_asset("./lambda"),
                                    role=execution_role,
                                    timeout=Duration.seconds(15),
                                    layers=[pillow_layer],
                                    environment={
                                        "DESTINATION_BUCKET_ARN": destination_bucket_arn,
                                        "RESIZE_HEIGHT": str(app_config.resize_height),
                                        "RESIZE_WIDTH": str(app_config.resize_width),
                                    })

        # 3. Attach Lambda to SQS source
        source_queue = sqs.Queue.from_queue_arn(self, id="SourceQueue", queue_arn=source_queue_arn)
        invoke_event_source = lambda_sources.SqsEventSource(source_queue)
        function.add_event_source(invoke_event_source)

        # 4. Export Function ARNs for further reference
        CfnOutput(self, "ResizerFunctionArn", value=function.function_arn)
