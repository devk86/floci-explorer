from botocore.exceptions import ClientError, UnknownServiceError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


class STSCollector(BaseCollector):
    service_name = "sts"

    def collect_sync(self) -> list[Resource]:
        try:
            identity = self.client().get_caller_identity()
            region = getattr(self.client().meta, "region_name", None)
        except UnknownServiceError:
            self.supported = False
            return []
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        account = identity.get("Account") or "local"
        return [
            Resource(
                id=f"sts:{account}",
                service="sts",
                resource_type="caller_identity",
                name=account,
                arn=identity.get("Arn"),
                region=region,
                status="active",
                metadata={"user_id": identity.get("UserId")},
                raw=identity,
            )
        ]
