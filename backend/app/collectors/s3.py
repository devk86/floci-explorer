from app.collectors.base import BaseCollector
from app.models.resource import Resource, isoformat_dt


class S3Collector(BaseCollector):
    service_name = "s3"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        response = client.list_buckets()
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for bucket in response.get("Buckets", []):
            name = bucket.get("Name")
            if not name:
                continue
            bucket_region = region
            try:
                loc = client.get_bucket_location(Bucket=name)
                constraint = loc.get("LocationConstraint")
                if constraint:
                    bucket_region = constraint
                elif constraint is None:
                    bucket_region = "us-east-1"
            except Exception:
                bucket_region = region
            resources.append(
                Resource(
                    id=f"s3:{name}",
                    service="s3",
                    resource_type="bucket",
                    name=name,
                    arn=f"arn:aws:s3:::{name}",
                    region=bucket_region,
                    status="available",
                    metadata={
                        "creation_date": isoformat_dt(bucket.get("CreationDate")),
                    },
                    raw=bucket,
                )
            )
        return resources
