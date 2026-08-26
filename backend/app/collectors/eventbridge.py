from botocore.exceptions import ClientError

from app.collectors.support import is_unsupported_api
from app.collectors.base import BaseCollector
from app.models.resource import Resource


class EventBridgeCollector(BaseCollector):
    service_name = "events"

    def collect_sync(self) -> list[Resource]:
        client = self.client("events")
        try:
            buses = self.paginate(client, "list_event_buses", "EventBuses")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for bus in buses:
            name = bus.get("Name")
            if not name:
                continue
            targets: list[dict] = []
            try:
                rules = self.paginate(client, "list_rules", "Rules", EventBusName=name)
                for rule in rules:
                    rule_name = rule.get("Name")
                    if not rule_name:
                        continue
                    listed = client.list_targets_by_rule(Rule=rule_name, EventBusName=name)
                    for target in listed.get("Targets", []):
                        targets.append(
                            {
                                "rule": rule_name,
                                "arn": target.get("Arn"),
                                "id": target.get("Id"),
                            }
                        )
            except Exception:
                targets = []
            resources.append(
                Resource(
                    id=f"events:{name}",
                    service="events",
                    resource_type="event_bus",
                    name=name,
                    arn=bus.get("Arn"),
                    region=region,
                    status="active",
                    metadata={"targets": targets},
                    raw=bus,
                )
            )
        return resources
