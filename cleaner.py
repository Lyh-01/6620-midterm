import os
import boto3
from datetime import datetime, timedelta

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["DYNAMODB_TABLE"]
DST_BUCKET = os.environ["DST_BUCKET"]
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    now = datetime.now()
    cutoff = now - timedelta(seconds=10)

    response = table.scan()
    for item in response.get("Items", []):
        if item['status'] == 'disowned':
            timestamp = datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S')
            if timestamp < cutoff:
                s3.delete_object(Bucket=DST_BUCKET, Key=item['object_key'])
                table.delete_item(Key={'object_key': item['object_key']})