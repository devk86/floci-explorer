from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class ELBv2Collector(BaseCollector):
    service_name = "elbv2"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            load_balancers = self.paginate(client, "describe_load_balancers", "LoadBalancers")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for alb in load_balancers:
            name = alb.get("LoadBalancerName")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"elbv2:{name}",
                    service="elbv2",
                    resource_type="load_balancer",
                    name=name,
                    arn=alb.get("LoadBalancerArn"),
                    region=region,
                    status=alb.get("State", {}).get("Code"),
                    metadata={"dns_name": alb.get("DNSName"), "scheme": alb.get("Scheme")},
                    raw=alb,
                )
            )
        return resources
