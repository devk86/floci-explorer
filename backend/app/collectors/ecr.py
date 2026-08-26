from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class ECRCollector(BaseCollector):
    service_name = "ecr"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            repos = self.paginate(client, "describe_repositories", "repositories")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for repo in repos:
            name = repo.get("repositoryName")
            if not name:
                continue
            resources.append(
                Resource(
                    id=f"ecr:{name}",
                    service="ecr",
                    resource_type="repository",
                    name=name,
                    arn=repo.get("repositoryArn"),
                    region=region,
                    status="available",
                    metadata={"uri": repo.get("repositoryUri")},
                    raw=repo,
                )
            )
        return resources
