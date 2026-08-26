from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class SecretsManagerCollector(BaseCollector):
    service_name = "secretsmanager"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            secrets = self.paginate(client, "list_secrets", "SecretList")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for secret in secrets:
            name = secret.get("Name")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"secretsmanager:{name}",
                    service="secretsmanager",
                    resource_type="secret",
                    name=name,
                    arn=secret.get("ARN"),
                    region=region,
                    status=secret.get("DeletedDate") and "deleted" or "active",
                    metadata={},
                    raw={k: v for k, v in secret.items() if k != "SecretString"},
                )
            )
        return resources
