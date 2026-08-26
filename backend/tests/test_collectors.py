from types import SimpleNamespace
from unittest.mock import MagicMock

from app.collectors.ec2 import EC2Collector
from app.collectors.lambda_ import LambdaCollector
from app.collectors.s3 import S3Collector
from app.floci.client import FlociClient


class FakeClient:
    def __init__(self, **methods):
        self.meta = SimpleNamespace(region_name="us-east-1")
        for name, impl in methods.items():
            setattr(self, name, impl)

    def get_paginator(self, _operation):
        raise RuntimeError("no paginator")


def _floci(mapping: dict) -> FlociClient:
    client = MagicMock(spec=FlociClient)
    client.get_client.side_effect = mapping.__getitem__
    return client


def test_ec2_normalizes_instance() -> None:
    instance = {
        "InstanceId": "i-abc",
        "InstanceType": "t3.micro",
        "ImageId": "ami-1",
        "SubnetId": "subnet-1",
        "PrivateIpAddress": "10.0.0.10",
        "PublicIpAddress": "1.2.3.4",
        "State": {"Name": "running"},
        "Tags": [{"Key": "Name", "Value": "web"}],
        "SecurityGroups": [{"GroupId": "sg-1"}],
    }
    fake = FakeClient(
        describe_instances=lambda: {"Reservations": [{"Instances": [instance]}]}
    )
    resources = EC2Collector(_floci({"ec2": fake})).collect_sync()
    assert len(resources) == 1
    resource = resources[0]
    assert resource.id == "ec2:i-abc"
    assert resource.name == "web"
    assert resource.status == "running"
    assert resource.metadata["instance_type"] == "t3.micro"


def test_s3_normalizes_bucket() -> None:
    fake = FakeClient(
        list_buckets=lambda: {"Buckets": [{"Name": "orders"}]},
        get_bucket_location=lambda Bucket: {"LocationConstraint": None},
    )
    resources = S3Collector(_floci({"s3": fake})).collect_sync()
    assert resources[0].id == "s3:orders"
    assert resources[0].arn == "arn:aws:s3:::orders"


def test_lambda_normalizes_function() -> None:
    fake = FakeClient(
        list_functions=lambda: {
            "Functions": [
                {
                    "FunctionName": "process-order",
                    "FunctionArn": "arn:aws:lambda:us-east-1:1:function:process-order",
                    "Runtime": "python3.12",
                    "Handler": "app.handler",
                    "MemorySize": 512,
                    "Timeout": 10,
                    "Role": "arn:aws:iam::1:role/lambda-role",
                    "State": "Active",
                    "Environment": {"Variables": {"TABLE_NAME": "orders"}},
                }
            ]
        },
        list_event_source_mappings=lambda: {
            "EventSourceMappings": [
                {
                    "FunctionArn": "arn:aws:lambda:us-east-1:1:function:process-order",
                    "EventSourceArn": "arn:aws:sqs:us-east-1:1:orders",
                }
            ]
        },
    )
    resources = LambdaCollector(_floci({"lambda": fake})).collect_sync()
    assert resources[0].id == "lambda:process-order"
    assert resources[0].metadata["environment"]["TABLE_NAME"] == "orders"
    assert "arn:aws:sqs:us-east-1:1:orders" in resources[0].metadata["event_source_arns"]
