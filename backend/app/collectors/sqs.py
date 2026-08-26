from app.collectors.base import BaseCollector
from app.models.resource import Resource


class SQSCollector(BaseCollector):
    service_name = "sqs"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        urls = self.paginate(client, "list_queues", "QueueUrls")
        # list_queues may return dict without pagination
        if not urls:
            response = client.list_queues()
            urls = response.get("QueueUrls") or []
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for url in urls:
            name = url.rsplit("/", 1)[-1]
            attributes: dict = {}
            try:
                attributes = client.get_queue_attributes(
                    QueueUrl=url, AttributeNames=["All"]
                ).get("Attributes", {})
            except Exception:
                attributes = {}
            resources.append(
                Resource(
                    id=f"sqs:{name}",
                    service="sqs",
                    resource_type="queue",
                    name=name,
                    arn=attributes.get("QueueArn"),
                    region=region,
                    status="active",
                    metadata={
                        "queue_url": url,
                        "queue_arn": attributes.get("QueueArn"),
                        "attributes": attributes,
                    },
                    raw={"QueueUrl": url, "Attributes": attributes},
                )
            )
        return resources
