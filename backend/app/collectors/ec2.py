from app.models.resource import Resource, isoformat_dt, tag_dict
from app.collectors.base import BaseCollector


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
                            "subnet_id": instance.get("SubnetId"),
                            "vpc_id": instance.get("VpcId"),
                            "private_ip": instance.get("PrivateIpAddress"),
                            "public_ip": instance.get("PublicIpAddress"),
                            "security_groups": [
                                sg.get("GroupId")
                                for sg in instance.get("SecurityGroups", [])
                                if sg.get("GroupId")
                            ],
                            "tags": tags,
                            "launch_time": isoformat_dt(instance.get("LaunchTime")),
                        },
                        raw=instance,
                    )
                )
        return resources
