from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class ECSCollector(BaseCollector):
    service_name = "ecs"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            cluster_arns = self.paginate(client, "list_clusters", "clusterArns")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for arn in cluster_arns:
            name = arn.rsplit("/", 1)[-1]
            resources.append(
                Resource(
                    id=f"ecs:{name}",
                    service="ecs",
                    resource_type="cluster",
                    name=name,
                    arn=arn,
                    region=region,
                    status="ACTIVE",
                    metadata={},
                    raw={"clusterArn": arn},
                )
            )
        return resources
