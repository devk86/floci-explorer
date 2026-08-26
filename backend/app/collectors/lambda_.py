from app.collectors.base import BaseCollector
from app.models.resource import Resource


class LambdaCollector(BaseCollector):
    service_name = "lambda"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        functions = self.paginate(client, "list_functions", "Functions")
        mappings = self._event_source_mappings(client)
        resources: list[Resource] = []
        region = getattr(client.meta, "region_name", None)
        for function in functions:
            name = function.get("FunctionName")
            if not name:
                continue
            env = ((function.get("Environment") or {}).get("Variables")) or {}
            resources.append(
                Resource(
                    id=f"lambda:{name}",
                    service="lambda",
                    resource_type="function",
                    name=name,
                    arn=function.get("FunctionArn"),
                    region=region,
                    status=function.get("State") or "Active",
                    metadata={
                        "runtime": function.get("Runtime"),
                        "handler": function.get("Handler"),
                        "memory": function.get("MemorySize"),
                        "timeout": function.get("Timeout"),
                        "role": function.get("Role"),
                        "environment": env,
                        "event_source_arns": mappings.get(function.get("FunctionArn"), [])
                        + mappings.get(name, []),
                    },
                    raw=function,
                )
            )
        return resources

    def _event_source_mappings(self, client) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {}
        try:
            mappings = self.paginate(client, "list_event_source_mappings", "EventSourceMappings")
        except Exception:
            return grouped
        for mapping in mappings:
            function_arn = mapping.get("FunctionArn") or mapping.get("FunctionName")
            source = mapping.get("EventSourceArn")
            if function_arn and source:
                grouped.setdefault(function_arn, []).append(source)
                name = function_arn.split(":")[-1]
                grouped.setdefault(name, []).append(source)
        return grouped
