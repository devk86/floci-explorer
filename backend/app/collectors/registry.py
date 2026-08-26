from app.collectors.apigateway import APIGatewayCollector
from app.collectors.cloudformation import CloudFormationCollector
from app.collectors.cloudwatch import CloudWatchCollector
from app.collectors.dynamodb import DynamoDBCollector
from app.collectors.ec2 import EC2Collector
from app.collectors.ecs import ECSCollector
from app.collectors.ecr import ECRCollector
from app.collectors.elbv2 import ELBv2Collector
from app.collectors.eventbridge import EventBridgeCollector
from app.collectors.generic import build_generic_collectors
from app.collectors.iam import IAMCollector
from app.collectors.kms import KMSCollector
from app.collectors.lambda_ import LambdaCollector
from app.collectors.route53 import Route53Collector
from app.collectors.s3 import S3Collector
from app.collectors.secretsmanager import SecretsManagerCollector
from app.collectors.sns import SNSCollector
from app.collectors.sqs import SQSCollector
from app.collectors.stepfunctions import StepFunctionsCollector
from app.collectors.sts import STSCollector
from app.collectors.vpc import VPCCollector
from app.collectors.base import BaseCollector
from app.floci.client import FlociClient

CORE_COLLECTORS: dict[str, type[BaseCollector]] = {
    "ec2": EC2Collector,
    "s3": S3Collector,
    "lambda": LambdaCollector,
    "dynamodb": DynamoDBCollector,
    "sqs": SQSCollector,
    "sns": SNSCollector,
    "iam": IAMCollector,
}

EXTENDED_COLLECTORS: dict[str, type[BaseCollector]] = {
    "apigateway": APIGatewayCollector,
    "events": EventBridgeCollector,
    "stepfunctions": StepFunctionsCollector,
    "logs": CloudWatchCollector,
    "kms": KMSCollector,
    "secretsmanager": SecretsManagerCollector,
    "vpc": VPCCollector,
    "ecs": ECSCollector,
    "ecr": ECRCollector,
    "elbv2": ELBv2Collector,
    "route53": Route53Collector,
    "cloudformation": CloudFormationCollector,
    "sts": STSCollector,
}

COLLECTORS: dict[str, type[BaseCollector]] = {
    **CORE_COLLECTORS,
    **EXTENDED_COLLECTORS,
    **build_generic_collectors(),
}


def build_collectors(floci_client: FlociClient) -> dict[str, BaseCollector]:
    return {name: cls(floci_client) for name, cls in COLLECTORS.items()}
