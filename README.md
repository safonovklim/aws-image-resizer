# AWS Image AutoResizer (Python)

This application automatically resizes every single image uploaded to the source S3 bucket.
New files will be uploaded to the same file name in the destination S3 bucket.

## See also

- [LICENSE.md](./LICENSE.md)
- [DevOps Long-term Strategy](./STRATEGY.md) 

## Components

- "Source" S3 bucket
- "Destination" S3 bucket
- SQS queue 
  - subscribed to S3 notification - OBJECT_CREATED
  - _Note: it does not include Dead-Letter Queue (DLQ), but it must be present in production-ready application to catch unexpected errors or unprocessed files. Operators must be notified if DLQ is NOT empty._
- Python Lambda Function (subscribed to SQS queue)
  - IAM (execution) Role for Python function that allows
    - reading from Source S3 bucket
    - writing to Destination S3 bucket
    - send/receive messages from SQS queue
    - publish Cloudwatch logs 

## Prerequisites

Before you run deploy/use this application, you must ensure the following:

1. Active AWS account (without outstanding bills)
2. Assumed AWS Administrator Role (`arn:aws:iam::aws:policy/AdministratorAccess`)
3. Installed [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [jq](https://jqlang.github.io/jq/download/) 

## 1. Deploy application

To deploy this project via MacOS / Linux, refer to [README.default.md](./README.default.md) or use:

### Step 1.1 - One-off setup (locally)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

### Step 1.2 - One-off CDK Bootstrap in your AWS Account 

```bash
cdk bootstrap
```

Expected output:

```
 ⏳  Bootstrapping environment aws://<AWS_ACCOUNT_ID>/us-east-1...
Trusted accounts for deployment: (none)
Trusted accounts for lookup: (none)
Using default execution policy of 'arn:aws:iam::aws:policy/AdministratorAccess'. Pass '--cloudformation-execution-policies' to customize.
CDKToolkit: creating CloudFormation changeset...
 ✅  Environment aws://<AWS_ACCOUNT_ID>/us-east-1 bootstrapped.
```

### Step 1.3 - Application Deployment

```bash
cdk synth
cdk deploy --all
```


## 2. Use Application

Now, after you deployed it, it's time to verify that resizing works correctly.

### Step 2.1 - Find Name of the "Source" bucket

Run:

```
> aws cloudformation describe-stacks | jq -r '.Stacks[] | select(.StackName | startswith("AwsImageAutoresizerStack")) | .Outputs[] | "\(.OutputKey): \(.OutputValue)"'
```

Expected output:

```
ResizerFunctionArn: arn:aws:lambda:us-east-1:764157184418:function:AwsImageAutoresizerStackLa-ResizerFunction51EC50EA-0MqOUWk3Xrwr
SourceBucketArn: arn:aws:s3:::awsimageautoresizerstackbucketsstac-source71e471f1-negcvfkmqdf9
DestinationBucketArn: arn:aws:s3:::awsimageautoresizerstackbucket-destination920a3c57-ewoyosmf6dmr
ResizingQueueArn: arn:aws:sqs:us-east-1:764157184418:AwsImageAutoresizerStackQueuesStack31F3FF06-ResizingQueue4B22CB3C-UWPe3y4HeeHe
```

Name of the source bucket is `awsimageautoresizerstackbucketsstac-source71e471f1-negcvfkmqdf9`

### Step 2.2 - Upload image to this source bucket

Replace variables and run the following;
```
export SOURCE_BUCKET_NAME=<PUT_YOUR_SOURCE_BUCKET_NAME>
aws s3 cp <local-file-path> s3://$BUCKET_NAME/<object-key>
```

Example:

```
> export BUCKET_NAME=awsimageautoresizerstackbucketsstac-source71e471f1-negcvfkmqdf9
> aws s3 cp /Users/klim/Desktop/Ooh/LivePass/logo_wide.png s3://$SOURCE_BUCKET_NAME/logo_wide.png

upload: ../../../Desktop/logo_wide.png to s3://awsimageautoresizerstackbucketsstac-source71e471f1-negcvfkmqdf9/logo_wide.png
```

### Step 2.3 - Download resized image from the destination bucket

Replace variables and run the following;
```
export DESTINATION_BUCKET_NAME=<PUT_YOUR_DESTINATION_BUCKET_NAME>
aws s3 cp s3://$BUCKET_NAME/<object-key> <local-file-path> 
```


Example: 
```
> export DESTINATION_BUCKET_NAME=awsimageautoresizerstackbucket-destination920a3c57-ewoyosmf6dmr
> aws s3 cp s3://$DESTINATION_BUCKET_NAME/logo_wide5.png /Users/klim/Desktop/resized_logo_wide5.png

download: s3://awsimageautoresizerstackbucket-destination920a3c57-ewoyosmf6dmr/logo_wide5.png to ../../../Desktop/resized_logo_wide5.png
```