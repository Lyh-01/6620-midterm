from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_s3 as s3
import aws_cdk as cdk

class S3Stack(Stack):
    def __init__(self, scope: cdk.App, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.bucket_src = s3.Bucket(self, "SrcBucket", removal_policy=cdk.RemovalPolicy.DESTROY)
        self.bucket_dst = s3.Bucket(self, "DstBucket", removal_policy=cdk.RemovalPolicy.DESTROY)

        # 输出桶的 ARNs
        CfnOutput(self, "SrcBucketArn", value=self.bucket_src.bucket_arn, export_name="SrcBucketArn")
        CfnOutput(self, "DstBucketArn", value=self.bucket_dst.bucket_arn, export_name="DstBucketArn")