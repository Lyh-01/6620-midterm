from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_dynamodb as dynamodb
import aws_cdk as cdk

class DynamoDBStack(Stack):
    def __init__(self, scope: cdk.App, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.table = dynamodb.Table(self, "TableT",
                                    partition_key=dynamodb.Attribute(name="object_key", type=dynamodb.AttributeType.STRING),
                                    sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
                                    removal_policy=cdk.RemovalPolicy.DESTROY)

        # 输出表名
        CfnOutput(self, "TableName", value=self.table.table_name, export_name="DynamoDBTableName")
