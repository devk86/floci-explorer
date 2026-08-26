from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class Route53Collector(BaseCollector):
    service_name = "route53"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            zones = self.paginate(client, "list_hosted_zones", "HostedZones")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        resources: list[Resource] = []
        for zone in zones:
            zone_id = (zone.get("Id") or "").split("/")[-1]
            name = zone.get("Name")
            if not zone_id:
                continue
            resources.append(
                Resource(
                    id=f"route53:{zone_id}",
                    service="route53",
                    resource_type="hosted_zone",
                    name=name,
                    arn=None,
                    region="global",
                    status="active",
                    metadata={"private": (zone.get("Config") or {}).get("PrivateZone")},
                    raw=zone,
                )
            )
        return resources
