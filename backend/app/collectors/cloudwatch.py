from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class CloudWatchCollector(BaseCollector):
    service_name = "logs"

    def collect_sync(self) -> list[Resource]:
        client = self.client("logs")
        try:
            groups = self.paginate(client, "describe_log_groups", "logGroups")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for group in groups:
            name = group.get("logGroupName")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"logs:{name}",
                    service="logs",
                    resource_type="log_group",
                    name=name,
                    arn=group.get("arn"),
                    region=region,
                    status="active",
                    metadata={"retention_days": group.get("retentionInDays")},
                    raw=group,
                )
            )
        return resources
