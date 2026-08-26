from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource, tag_dict


class VPCCollector(BaseCollector):
    service_name = "vpc"

    def collect_sync(self) -> list[Resource]:
        client = self.client("ec2")
        try:
            vpcs = self.paginate(client, "describe_vpcs", "Vpcs")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for vpc in vpcs:
            vpc_id = vpc.get("VpcId")
            if not vpc_id:
                continue
            tags = tag_dict(vpc.get("Tags"))
            resources.append(
                Resource(
                    id=f"vpc:{vpc_id}",
                    service="vpc",
                    resource_type="vpc",
                    name=tags.get("Name") or vpc_id,
                    arn=None,
                    region=region,
                    status=vpc.get("State"),
                    metadata={"cidr": vpc.get("CidrBlock"), "is_default": vpc.get("IsDefault"), "tags": tags},
                    raw=vpc,
                )
            )
        try:
            subnets = self.paginate(client, "describe_subnets", "Subnets")
        except Exception:
            subnets = []
        for subnet in subnets:
            subnet_id = subnet.get("SubnetId")
            if not subnet_id:
                continue
            tags = tag_dict(subnet.get("Tags"))
            resources.append(
                Resource(
                    id=f"vpc:subnet:{subnet_id}",
                    service="vpc",
                    resource_type="subnet",
                    name=tags.get("Name") or subnet_id,
                    region=region,
                    status=subnet.get("State"),
                    metadata={
                        "vpc_id": subnet.get("VpcId"),
                        "cidr": subnet.get("CidrBlock"),
                        "az": subnet.get("AvailabilityZone"),
                        "tags": tags,
                    },
                    raw=subnet,
                )
            )
        try:
            groups = self.paginate(client, "describe_security_groups", "SecurityGroups")
        except Exception:
            groups = []
        for group in groups:
            group_id = group.get("GroupId")
            if not group_id:
                continue
            resources.append(
                Resource(
                    id=f"vpc:sg:{group_id}",
                    service="vpc",
                    resource_type="security_group",
                    name=group.get("GroupName") or group_id,
                    region=region,
                    status="available",
                    metadata={"vpc_id": group.get("VpcId"), "group_id": group_id},
                    raw=group,
                )
            )
        return resources
