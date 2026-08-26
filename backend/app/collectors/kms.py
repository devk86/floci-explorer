from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class KMSCollector(BaseCollector):
    service_name = "kms"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            keys = self.paginate(client, "list_keys", "Keys")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for key in keys:
            key_id = key.get("KeyId")
            if not key_id:
                continue
            resources.append(
                Resource(
                    id=f"kms:{key_id}",
                    service="kms",
                    resource_type="key",
                    name=key_id,
                    arn=key.get("KeyArn"),
                    region=region,
                    status="enabled",
                    metadata={},
                    raw=key,
                )
            )
        return resources
