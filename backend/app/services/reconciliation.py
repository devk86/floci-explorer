from __future__ import annotations

from typing import Any

from app.models.resource import Resource
from app.services.terraform import TerraformStateParser

MATCH = "MATCH"
MISSING_IN_FLOCI = "MISSING_IN_FLOCI"
MISSING_IN_TERRAFORM = "MISSING_IN_TERRAFORM"
DIFFERENT_CONFIGURATION = "DIFFERENT_CONFIGURATION"
FLOCI_ONLY = "Floci only"
TERRAFORM_ONLY = "Terraform only"
MATCHED = "Matched"


class ReconciliationService:
    def __init__(self, parser: TerraformStateParser | None = None) -> None:
        self.parser = parser or TerraformStateParser()

    def classify(self, floci: list[Resource], terraform: list[Resource]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        used_tf: set[str] = set()
        for resource in floci:
            match = self._match(resource, terraform)
            if match:
                used_tf.add(match.id)
                drift = self._drift(resource, match)
                rows.append(
                    {
                        "resource": resource.name or resource.id,
                        "service": resource.service,
                        "presence": MATCHED,
                        "status": DIFFERENT_CONFIGURATION if drift else MATCH,
                        "floci": resource.metadata,
                        "terraform": (match.metadata or {}).get("attributes") or {},
                        "differences": drift,
                    }
                )
            else:
                rows.append(
                    {
                        "resource": resource.name or resource.id,
                        "service": resource.service,
                        "presence": FLOCI_ONLY,
                        "status": MISSING_IN_TERRAFORM,
                        "floci": resource.metadata,
                        "terraform": {},
                        "differences": [],
                    }
                )
        for tf_resource in terraform:
            if tf_resource.id in used_tf:
                continue
            rows.append(
                {
                    "resource": tf_resource.name or tf_resource.id,
                    "service": tf_resource.service,
                    "presence": TERRAFORM_ONLY,
                    "status": MISSING_IN_FLOCI,
                    "floci": {},
                    "terraform": (tf_resource.metadata or {}).get("attributes") or {},
                    "differences": [],
                }
            )
        return rows

    def _match(self, resource: Resource, terraform: list[Resource]) -> Resource | None:
        for candidate in terraform:
            if candidate.service != resource.service:
                continue
            if candidate.name == resource.name or candidate.name == resource.id.split(":")[-1]:
                return candidate
        return None

    def _drift(self, floci: Resource, terraform: Resource) -> list[dict[str, Any]]:
        attrs = (terraform.metadata or {}).get("attributes") or {}
        compared = {
            "memory": ("memory", "memory_size"),
            "timeout": ("timeout", "timeout"),
            "runtime": ("runtime", "runtime"),
            "instance_type": ("instance_type", "instance_type"),
        }
        diffs: list[dict[str, Any]] = []
        for label, (meta_key, tf_key) in compared.items():
            left = floci.metadata.get(meta_key)
            right = attrs.get(tf_key)
            if left is None or right is None:
                continue
            if str(left) != str(right):
                diffs.append({"field": label, "floci": left, "terraform": right})
        return diffs
