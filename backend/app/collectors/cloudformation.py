from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class CloudFormationCollector(BaseCollector):
    service_name = "cloudformation"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            stacks = self.paginate(client, "list_stacks", "StackSummaries")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for stack in stacks:
            name = stack.get("StackName")
            if not name:
                continue
            status = stack.get("StackStatus")
            if status and str(status).endswith("DELETE_COMPLETE"):
                continue
            resources.append(
                Resource(
                    id=f"cloudformation:{name}",
                    service="cloudformation",
                    resource_type="stack",
                    name=name,
                    arn=stack.get("StackId"),
                    region=region,
                    status=status,
                    metadata={},
                    raw=stack,
                )
            )
        return resources
