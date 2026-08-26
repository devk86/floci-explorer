from __future__ import annotations

import json

from app.dependencies.parsers import (
    BUCKET_ENV_KEYS,
    TABLE_ENV_KEYS,
    env_values,
    lambda_arn_from_integration_uri,
    name_from_arn,
)
from app.models.relationship import Relationship
from app.models.resource import Resource


def _index(resources: list[Resource]) -> dict[str, Resource]:
    indexed: dict[str, Resource] = {}
    for resource in resources:
        indexed[resource.id] = resource
        if resource.arn:
            indexed[resource.arn] = resource
        if resource.name:
            indexed[f"{resource.service}:{resource.name}"] = resource
            indexed[resource.name] = resource
    return indexed


def _rel(
    source: str,
    target: str,
    relationship: str,
    confidence: float,
    source_field: str | None,
) -> Relationship:
    return Relationship(
        source=source,
        target=target,
        relationship=relationship,
        confidence=confidence,
        source_field=source_field,
    )


def sqs_triggers_lambda(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    lambdas = [item for item in resources if item.service == "lambda"]
    for function in lambdas:
        for arn in function.metadata.get("event_source_arns") or []:
            if ":sqs:" not in arn:
                continue
            queue = index.get(arn) or index.get(f"sqs:{name_from_arn(arn)}")
            if queue:
                edges.append(
                    _rel(queue.id, function.id, "triggers", 1.0, "event_source_mappings")
                )
    return edges


def sns_publishes_to_sqs(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for topic in resources:
        if topic.service != "sns":
            continue
        for sub in topic.metadata.get("subscriptions") or []:
            if (sub.get("Protocol") or "").lower() != "sqs":
                continue
            endpoint = sub.get("Endpoint") or ""
            queue = index.get(endpoint) or index.get(f"sqs:{name_from_arn(endpoint)}")
            if queue:
                edges.append(_rel(topic.id, queue.id, "publishes_to", 1.0, "subscriptions"))
    return edges


def lambda_to_dynamodb(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for function in resources:
        if function.service != "lambda":
            continue
        for key, value in env_values(function, TABLE_ENV_KEYS):
            table = index.get(value) or index.get(f"dynamodb:{name_from_arn(value)}")
            if table and table.service == "dynamodb":
                edges.append(
                    _rel(
                        function.id,
                        table.id,
                        "reads_from_or_writes_to",
                        0.7,
                        f"environment.{key}",
                    )
                )
    return edges


def lambda_to_s3(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for function in resources:
        if function.service != "lambda":
            continue
        for key, value in env_values(function, BUCKET_ENV_KEYS):
            bucket_name = value.replace("arn:aws:s3:::", "").split("/")[0]
            bucket = index.get(f"s3:{bucket_name}") or index.get(bucket_name)
            if bucket and bucket.service == "s3":
                edges.append(
                    _rel(
                        function.id,
                        bucket.id,
                        "reads_from_or_writes_to",
                        0.7,
                        f"environment.{key}",
                    )
                )
    return edges


def iam_execution_role(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for function in resources:
        if function.service != "lambda":
            continue
        role_arn = function.metadata.get("role")
        if not role_arn:
            continue
        role = index.get(role_arn) or index.get(f"iam:role:{name_from_arn(role_arn)}")
        if role:
            edges.append(_rel(role.id, function.id, "execution_role", 1.0, "role"))
    return edges


def apigateway_to_lambda(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for api in resources:
        if api.service != "apigateway":
            continue
        for integration in api.metadata.get("integrations") or []:
            uri = integration.get("uri") or ""
            arn = lambda_arn_from_integration_uri(uri)
            if not arn:
                continue
            function = index.get(arn) or index.get(f"lambda:{name_from_arn(arn)}")
            if function:
                edges.append(_rel(api.id, function.id, "invokes", 1.0, "integrations"))
    return edges


def eventbridge_to_lambda(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for bus in resources:
        if bus.service != "events":
            continue
        for target in bus.metadata.get("targets") or []:
            arn = target.get("arn") or ""
            if ":lambda:" not in arn:
                continue
            function = index.get(arn) or index.get(f"lambda:{name_from_arn(arn)}")
            if function:
                edges.append(_rel(bus.id, function.id, "invokes", 1.0, "targets"))
    return edges


def stepfunctions_to_lambda(resources: list[Resource], index: dict[str, Resource]) -> list[Relationship]:
    edges: list[Relationship] = []
    for machine in resources:
        if machine.service != "stepfunctions":
            continue
        definition = machine.metadata.get("definition") or ""
        if isinstance(definition, dict):
            text = json.dumps(definition)
        else:
            text = str(definition)
        for resource in resources:
            if resource.service != "lambda" or not resource.arn:
                continue
            if resource.arn in text or (resource.name and resource.name in text):
                # Name-only match is weaker and only used with function: prefix
                if resource.arn in text:
                    edges.append(
                        _rel(machine.id, resource.id, "invokes", 1.0, "definition")
                    )
                elif f"function:{resource.name}" in text:
                    edges.append(
                        _rel(machine.id, resource.id, "invokes", 0.9, "definition")
                    )
    return edges


RULES = [
    sqs_triggers_lambda,
    sns_publishes_to_sqs,
    lambda_to_dynamodb,
    lambda_to_s3,
    iam_execution_role,
    apigateway_to_lambda,
    eventbridge_to_lambda,
    stepfunctions_to_lambda,
]
