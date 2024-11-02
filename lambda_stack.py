from aws_cdk import Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda_event_sources as sources
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import Fn
import aws_cdk as cdk

class LambdaStack(Stack):
    def __init__(self, scope: cdk.App, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 导入 S3 桶和 DynamoDB 表的 ARNs
        src_bucket_arn = Fn.import_value("SrcBucketArn")
        dst_bucket_arn = Fn.import_value("DstBucketArn")
        table_name = Fn.import_value("DynamoDBTableName")

        # 从 ARN 创建 S3 桶引用
        self.bucket_src = s3.Bucket.from_bucket_arn(self, "ImportedSrcBucket", src_bucket_arn)
        self.bucket_dst = s3.Bucket.from_bucket_arn(self, "ImportedDstBucket", dst_bucket_arn)

        # 从表名创建 DynamoDB 表引用
        self.table = dynamodb.Table.from_table_name(self, "ImportedTable", table_name)

        # Replicator Lambda 函数
        self.replicator_fn = lambda_.Function(
            self, "ReplicatorFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="replicator.handler",
            code=lambda_.Code.from_asset("lambda_functions"),
            environment={
                "SRC_BUCKET": self.bucket_src.bucket_name,
                "DST_BUCKET": self.bucket_dst.bucket_name,
                "DYNAMODB_TABLE": self.table.table_name
            }
        )
        self.bucket_src.grant_read(self.replicator_fn)
        self.bucket_dst.grant_write(self.replicator_fn)
        self.table.grant_read_write_data(self.replicator_fn)

        # S3 事件源触发器
        self.replicator_fn.add_event_source(
            sources.S3EventSource(self.bucket_src, events=[s3.EventType.OBJECT_CREATED, s3.EventType.OBJECT_REMOVED])
        )

        # Cleaner Lambda 函数
        self.cleaner_fn = lambda_.Function(
            self, "CleanerFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="cleaner.handler",
            code=lambda_.Code.from_asset("lambda_functions"),
            environment={
                "DYNAMODB_TABLE": self.table.table_name,
                "DST_BUCKET": self.bucket_dst.bucket_name
            }
        )
        self.bucket_dst.grant_delete(self.cleaner_fn)
        self.table.grant_read_write_data(self.cleaner_fn)

        # 设置 Cleaner 的定时触发规则
        rule = events.Rule(
            self, "CleanerSchedule",
            schedule=events.Schedule.rate(cdk.Duration.minutes(1))
        )
        rule.add_target(targets.LambdaFunction(self.cleaner_fn))