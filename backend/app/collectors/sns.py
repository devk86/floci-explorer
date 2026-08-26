from app.collectors.base import BaseCollector
from app.models.resource import Resource


class SNSCollector(BaseCollector):
    service_name = "sns"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        topics = self.paginate(client, "list_topics", "Topics")
        subscriptions = []
        try:
            subscriptions = self.paginate(client, "list_subscriptions", "Subscriptions")
        except Exception:
            subscriptions = []
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for topic in topics:
            arn = topic.get("TopicArn")
            if not arn:
                continue
            name = arn.rsplit(":", 1)[-1]
            topic_subs = [
                sub
                for sub in subscriptions
                if sub.get("TopicArn") == arn
            ]
            resources.append(
                Resource(
                    id=f"sns:{name}",
                    service="sns",
                    resource_type="topic",
                    name=name,
                    arn=arn,
                    region=region,
                    status="active",
                    metadata={"subscriptions": topic_subs},
                    raw=topic,
                )
            )
        return resources
