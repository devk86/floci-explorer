from typing import Any

from app.models.resource import Resource, isoformat_dt, tag_dict
from app.collectors.base import BaseCollector


def _security_group_ids(item: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for group in item.get("SecurityGroups") or item.get("Groups") or []:
        if isinstance(group, str) and group:
            ids.append(group)
            continue
        if isinstance(group, dict):
            group_id = group.get("GroupId")
            if group_id:
                ids.append(str(group_id))
    return ids


class EC2Collector(BaseCollector):
    service_name = "ec2"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        reservations = self.paginate(client, "describe_instances", "Reservations")
        resources: list[Resource] = []
        region = getattr(client, "meta", None)
        region_name = region.region_name if region else None
        for reservation in reservations:
            for instance in reservation.get("Instances", []):
                instance_id = instance.get("InstanceId")
                if not instance_id:
                    continue
                tags = tag_dict(instance.get("Tags"))
                security_groups = _security_group_ids(instance)
                subnet_id = instance.get("SubnetId")
                vpc_id = instance.get("VpcId")
                if not subnet_id or not vpc_id or not security_groups:
                    for interface in instance.get("NetworkInterfaces") or []:
                        subnet_id = subnet_id or interface.get("SubnetId")
                        vpc_id = vpc_id or interface.get("VpcId")
                        for group_id in _security_group_ids(interface):
                            if group_id not in security_groups:
                                security_groups.append(group_id)
                resources.append(
                    Resource(
                        id=f"ec2:{instance_id}",
                        service="ec2",
                        resource_type="instance",
                        name=tags.get("Name") or instance_id,
                        arn=instance.get("InstanceArn"),
                        region=instance.get("Placement", {}).get("AvailabilityZone")
                        and region_name
                        or region_name,
                        status=(instance.get("State") or {}).get("Name"),
                        metadata={
                            "instance_id": instance_id,
                            "instance_type": instance.get("InstanceType"),
                            "image_id": instance.get("ImageId"),
                            "subnet_id": subnet_id,
                            "vpc_id": vpc_id,
                            "private_ip": instance.get("PrivateIpAddress"),
                            "public_ip": instance.get("PublicIpAddress"),
                            "security_groups": security_groups,
                            "tags": tags,
                            "launch_time": isoformat_dt(instance.get("LaunchTime")),
                        },
                        raw=instance,
                    )
                )
        return resources
