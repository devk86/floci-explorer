from app.dependencies.engine import DependencyEngine
from app.models.resource import Resource


def test_sqs_triggers_lambda() -> None:
    resources = [
        Resource(
            id="sqs:orders",
            service="sqs",
            resource_type="queue",
            name="orders",
            arn="arn:aws:sqs:us-east-1:1:orders",
        ),
        Resource(
            id="lambda:process-order",
            service="lambda",
            resource_type="function",
            name="process-order",
            metadata={"event_source_arns": ["arn:aws:sqs:us-east-1:1:orders"]},
        ),
    ]
    rels = DependencyEngine().build(resources)
    assert any(rel.relationship == "triggers" and rel.confidence == 1.0 for rel in rels)


def test_sns_to_sqs() -> None:
    resources = [
        Resource(
            id="sns:events",
            service="sns",
            resource_type="topic",
            name="events",
            arn="arn:aws:sns:us-east-1:1:events",
            metadata={
                "subscriptions": [
                    {
                        "Protocol": "sqs",
                        "Endpoint": "arn:aws:sqs:us-east-1:1:orders",
                        "TopicArn": "arn:aws:sns:us-east-1:1:events",
                    }
                ]
            },
        ),
        Resource(
            id="sqs:orders",
            service="sqs",
            resource_type="queue",
            name="orders",
            arn="arn:aws:sqs:us-east-1:1:orders",
        ),
    ]
    rels = DependencyEngine().build(resources)
    assert any(rel.relationship == "publishes_to" for rel in rels)


def test_lambda_env_inference_does_not_invent_targets() -> None:
    resources = [
        Resource(
            id="lambda:process-order",
            service="lambda",
            resource_type="function",
            name="process-order",
            metadata={"environment": {"TABLE_NAME": "missing-table", "BUCKET_NAME": "orders"}},
        ),
        Resource(id="s3:orders", service="s3", resource_type="bucket", name="orders"),
    ]
    rels = DependencyEngine().build(resources)
    assert any(rel.target == "s3:orders" for rel in rels)
    assert all(rel.target != "dynamodb:missing-table" for rel in rels)


def test_iam_execution_role() -> None:
    resources = [
        Resource(
            id="iam:role:lambda-role",
            service="iam",
            resource_type="role",
            name="lambda-role",
            arn="arn:aws:iam::1:role/lambda-role",
        ),
        Resource(
            id="lambda:process-order",
            service="lambda",
            resource_type="function",
            name="process-order",
            metadata={"role": "arn:aws:iam::1:role/lambda-role"},
        ),
    ]
    rels = DependencyEngine().build(resources)
    assert any(rel.relationship == "execution_role" and rel.confidence == 1.0 for rel in rels)
