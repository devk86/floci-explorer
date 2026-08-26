from app.collectors.base import BaseCollector
from app.models.resource import Resource


class DynamoDBCollector(BaseCollector):
    service_name = "dynamodb"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        table_names = self.paginate(client, "list_tables", "TableNames")
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for name in table_names:
            description: dict = {}
            try:
                description = client.describe_table(TableName=name).get("Table", {})
            except Exception:
                description = {"TableName": name}
            key_schema = description.get("KeySchema") or []
            partition = next((k["AttributeName"] for k in key_schema if k.get("KeyType") == "HASH"), None)
            sort = next((k["AttributeName"] for k in key_schema if k.get("KeyType") == "RANGE"), None)
            resources.append(
                Resource(
                    id=f"dynamodb:{name}",
                    service="dynamodb",
                    resource_type="table",
                    name=name,
                    arn=description.get("TableArn"),
                    region=region,
                    status=description.get("TableStatus") or "ACTIVE",
                    metadata={
                        "partition_key": partition,
                        "sort_key": sort,
                        "billing_mode": (description.get("BillingModeSummary") or {}).get(
                            "BillingMode"
                        ),
                        "item_count": description.get("ItemCount"),
                    },
                    raw=description or {"TableName": name},
                )
            )
        return resources
