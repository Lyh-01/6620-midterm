from aws_cdk import App, Environment
from s3_stack import S3Stack
from dynamodb_stack import DynamoDBStack
from lambda_stack import LambdaStack

app = App()

# 设置环境
env = Environment(account="376129856599", region="us-east-1")

# 创建 S3 和 DynamoDB 堆栈
s3_stack = S3Stack(app, "S3Stack", env=env)
dynamodb_stack = DynamoDBStack(app, "DynamoDBStack", env=env)

# 创建 Lambda 堆栈
lambda_stack = LambdaStack(app, "LambdaStack", env=env)

app.synth()