from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.resource import Resource

TF_SERVICE_MAP = {
    "aws_instance": ("ec2", "instance"),
    "aws_s3_bucket": ("s3", "bucket"),
    "aws_lambda_function": ("lambda", "function"),
    "aws_dynamodb_table": ("dynamodb", "table"),
    "aws_sqs_queue": ("sqs", "queue"),
    "aws_sns_topic": ("sns", "topic"),
    "aws_iam_role": ("iam", "role"),
    "aws_api_gateway_rest_api": ("apigateway", "rest_api"),
    "aws_cloudwatch_event_bus": ("events", "event_bus"),
    "aws_sfn_state_machine": ("stepfunctions", "state_machine"),
}


class TerraformStateParser:
    def parse_file(self, path: str | Path) -> list[Resource]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return self.parse(data)

    def parse(self, state: dict[str, Any]) -> list[Resource]:
        resources: list[Resource] = []
        for module in _iter_modules(state):
            for resource in module.get("resources", []):
                resources.extend(self._from_resource(resource))
        return resources

    def _from_resource(self, resource: dict[str, Any]) -> list[Resource]:
        tf_type = resource.get("type") or ""
        name = resource.get("name") or ""
        service, resource_type = TF_SERVICE_MAP.get(tf_type, ("terraform", tf_type or "resource"))
        items: list[Resource] = []
        for index, instance in enumerate(resource.get("instances") or [{}]):
            attrs = instance.get("attributes") or {}
            instance_name = attrs.get("id") or attrs.get("function_name") or attrs.get("name") or name
            depends = instance.get("dependencies") or resource.get("depends_on") or []
            items.append(
                Resource(
                    id=f"tf:{tf_type}.{name}[{index}]",
                    service=service,
                    resource_type=resource_type,
                    name=str(instance_name),
                    arn=attrs.get("arn"),
                    region=attrs.get("region"),
                    status="terraform",
                    metadata={
                        "address": f"{tf_type}.{name}",
                        "terraform_type": tf_type,
                        "dependencies": depends,
                        "attributes": attrs,
                    },
                    raw=instance,
                    origin="terraform",
                )
            )
        return items


def _iter_modules(state: dict[str, Any]) -> list[dict[str, Any]]:
    values = state.get("values") or state
    root = values.get("root_module") or values
    modules = [root]
    modules.extend(root.get("child_modules") or [])
    # terraform state v4 uses resources at top-level
    if "resources" in state and "values" not in state:
        return [state]
    return modules
