from types import SimpleNamespace
from unittest.mock import MagicMock

from app.collectors.dynamodb import DynamoDBCollector
from app.collectors.iam import IAMCollector
from app.collectors.sns import SNSCollector
from app.collectors.sqs import SQSCollector
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


def test_dynamodb_table() -> None:
    fake = FakeClient(
        list_tables=lambda: {"TableNames": ["orders"]},
        describe_table=lambda TableName: {
            "Table": {
                "TableName": TableName,
                "TableArn": "arn:aws:dynamodb:us-east-1:1:table/orders",
                "TableStatus": "ACTIVE",
                "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
                "BillingModeSummary": {"BillingMode": "PAY_PER_REQUEST"},
            }
        },
    )
    resources = DynamoDBCollector(_floci({"dynamodb": fake})).collect_sync()
    assert resources[0].id == "dynamodb:orders"
    assert resources[0].metadata["partition_key"] == "id"


def test_sqs_queue() -> None:
    fake = FakeClient(
        list_queues=lambda: {"QueueUrls": ["https://localhost/000/orders"]},
        get_queue_attributes=lambda **kwargs: {
            "Attributes": {"QueueArn": "arn:aws:sqs:us-east-1:1:orders"}
        },
    )
    resources = SQSCollector(_floci({"sqs": fake})).collect_sync()
    assert resources[0].id == "sqs:orders"


def test_sns_topic() -> None:
    fake = FakeClient(
        list_topics=lambda: {"Topics": [{"TopicArn": "arn:aws:sns:us-east-1:1:events"}]},
        list_subscriptions=lambda: {"Subscriptions": []},
    )
    resources = SNSCollector(_floci({"sns": fake})).collect_sync()
    assert resources[0].id == "sns:events"


def test_iam_role() -> None:
    fake = FakeClient(
        list_roles=lambda: {"Roles": [{"RoleName": "lambda-role", "Arn": "arn:aws:iam::1:role/lambda-role"}]},
        list_policies=lambda **kwargs: {"Policies": []},
    )
    resources = IAMCollector(_floci({"iam": fake})).collect_sync()
    assert resources[0].id == "iam:role:lambda-role"
