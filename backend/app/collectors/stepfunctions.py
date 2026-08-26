from botocore.exceptions import ClientError

from app.collectors.support import is_unsupported_api
from app.collectors.base import BaseCollector
from app.models.resource import Resource


class StepFunctionsCollector(BaseCollector):
    service_name = "stepfunctions"

    def collect_sync(self) -> list[Resource]:
        client = self.client()
        try:
            machines = self.paginate(client, "list_state_machines", "stateMachines")
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        region = getattr(client.meta, "region_name", None)
        resources: list[Resource] = []
        for machine in machines:
            arn = machine.get("stateMachineArn")
            name = machine.get("name")
            if not arn or not name:
                continue
            definition = ""
            try:
                described = client.describe_state_machine(stateMachineArn=arn)
                definition = described.get("definition") or ""
            except Exception:
                definition = ""
            resources.append(
                Resource(
                    id=f"stepfunctions:{name}",
                    service="stepfunctions",
                    resource_type="state_machine",
                    name=name,
                    arn=arn,
                    region=region,
                    status=machine.get("status") or "ACTIVE",
                    metadata={"definition": definition},
                    raw=machine,
                )
            )
        return resources
