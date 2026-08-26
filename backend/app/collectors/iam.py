from app.collectors.base import BaseCollector
from app.models.resource import Resource, tag_dict


class IAMCollector(BaseCollector):
    service_name = "iam"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        resources: list[Resource] = []
        roles = self.paginate(client, "list_roles", "Roles")
        for role in roles:
            name = role.get("RoleName")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"iam:role:{name}",
                    service="iam",
                    resource_type="role",
                    name=name,
                    arn=role.get("Arn"),
                    region="global",
                    status="active",
                    metadata={
                        "path": role.get("Path"),
                        "description": role.get("Description"),
                        "tags": tag_dict(role.get("Tags")),
                    },
                    raw=role,
                )
            )
        try:
            policies = self.paginate(client, "list_policies", "Policies", Scope="Local")
        except Exception:
            policies = []
        for policy in policies:
            name = policy.get("PolicyName")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"iam:policy:{name}",
                    service="iam",
                    resource_type="policy",
                    name=name,
                    arn=policy.get("Arn"),
                    region="global",
                    status="active",
                    metadata={"attachment_count": policy.get("AttachmentCount")},
                    raw=policy,
                )
            )
        return resources
