import os
import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

SRC_BUCKET = os.environ["SRC_BUCKET"]
DST_BUCKET = os.environ["DST_BUCKET"]
TABLE_NAME = os.environ["DYNAMODB_TABLE"]
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    for record in event['Records']:
        object_key = record['s3']['object']['key']
        if record['eventName'].startswith("ObjectCreated"):
            copy_source = {'Bucket': SRC_BUCKET, 'Key': object_key}
            s3.copy_object(CopySource=copy_source, Bucket=DST_BUCKET, Key=object_key)
            table.put_item(Item={'object_key': object_key, 'timestamp': str(context.aws_request_id), 'status': 'copied'})
        elif record['eventName'].startswith("ObjectRemoved"):
            s3.delete_object(Bucket=DST_BUCKET, Key=object_key)
            table.update_item(Key={'object_key': object_key},
                              UpdateExpression="set status = :s",
                              ExpressionAttributeValues={':s': 'disowned'})