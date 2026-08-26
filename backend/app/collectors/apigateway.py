from botocore.exceptions import ClientError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class APIGatewayCollector(BaseCollector):
    service_name = "apigateway"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            apis = self.paginate(client, "get_rest_apis", "items")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for api in apis:
            api_id = api.get("id")
            if not api_id:
                continue
            integrations: list[dict] = []
            try:
                resources_list = self.paginate(
                    client, "get_resources", "items", restApiId=api_id
                )
                for item in resources_list:
                    for method, config in (item.get("resourceMethods") or {}).items():
                        uri = ((config.get("methodIntegration") or {}).get("uri")) or ""
                        if uri:
                            integrations.append({"method": method, "uri": uri})
            except Exception:
                integrations = []
            resources.append(
                Resource(
                    id=f"apigateway:{api_id}",
                    service="apigateway",
                    resource_type="rest_api",
                    name=api.get("name") or api_id,
                    arn=None,
                    region=region,
                    status="available",
                    metadata={"integrations": integrations},
                    raw=api,
                )
            )
        return resources
