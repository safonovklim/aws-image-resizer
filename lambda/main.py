import boto3
import json
import os
from PIL import Image


s3_client = boto3.client('s3')

def handler(event, context):
    print("Lambda Invoked")
    print(event)

    resize_width = int(os.getenv("RESIZE_WIDTH", "200"))
    resize_height = int(os.getenv("RESIZE_HEIGHT", "200"))
    destination_bucket_arn = os.getenv("DESTINATION_BUCKET_ARN")
    destination_bucket_name = destination_bucket_arn.split(':')[-1]

    for record in event['Records']:
        # Step 1 - Fetch message
        message = record['body']
        print(f"Step 1 - Received message: {message}")

        # Step 2 - Parse the message to get the S3 bucket and object key
        s3_event = json.loads(message)
        bucket_name = s3_event['Records'][0]['s3']['bucket']['name']
        object_key = s3_event['Records'][0]['s3']['object']['key']
        print(f"Step 2 - Received S3 file: {bucket_name} / {object_key}")

        # Step 3 - Download the file from S3 to /tmp folder
        download_path = f"/tmp/{object_key}"
        s3_client.download_file(bucket_name, object_key, download_path)
        print(f"Step 3 - Downloaded {object_key} from {bucket_name} to {download_path}")

        # Step 4 - Resize/Crop
        resized_path = f"/tmp/resized-{object_key.split('/')[-1]}"
        with Image.open(download_path) as image:
            image.thumbnail((resize_width, resize_height))
            image.save(resized_path)
            print(f"Step 4 - Resized image saved to {resized_path}")

        # Step 5 - Upload
        s3_client.upload_file(resized_path, destination_bucket_name, object_key)
        print(f"Step 5 - Uploaded resized image to {destination_bucket_name}/{object_key}")
