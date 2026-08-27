from app.collectors.base import BaseCollector
from app.models.resource import Resource, tag_dict


class IAMCollector(BaseCollector):
    service_name = "iam"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        resources: list[Resource] = []
        try:
            roles = self.paginate(client, "list_roles", "Roles")
        except Exception:
            roles = []
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
        try:
            users = self.paginate(client, "list_users", "Users")
        except Exception:
            users = []
        for user in users:
            name = user.get("UserName")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"iam:user:{name}",
                    service="iam",
                    resource_type="user",
                    name=name,
                    arn=user.get("Arn"),
                    region="global",
                    status="active",
                    metadata={
                        "path": user.get("Path"),
                        "user_id": user.get("UserId"),
                        "create_date": str(user.get("CreateDate")) if user.get("CreateDate") else None,
                        "tags": tag_dict(user.get("Tags")),
                    },
                    raw=user,
                )
            )
        return resources
