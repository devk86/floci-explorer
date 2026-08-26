from app.services.reconciliation import DIFFERENT_CONFIGURATION, MATCH, ReconciliationService
from app.services.terraform import TerraformStateParser
from app.models.resource import Resource


def test_parse_terraform_state() -> None:
    state = {
        "resources": [
            {
                "type": "aws_lambda_function",
                "name": "process_order",
                "instances": [
                    {
                        "attributes": {
                            "function_name": "process-order",
                            "memory_size": 512,
                            "arn": "arn:aws:lambda:us-east-1:1:function:process-order",
                        }
                    }
                ],
            }
        ]
    }
    resources = TerraformStateParser().parse(state)
    assert resources[0].origin == "terraform"
    assert resources[0].name == "process-order"


def test_drift_detection() -> None:
    floci = [
        Resource(
            id="lambda:process-order",
            service="lambda",
            resource_type="function",
            name="process-order",
            metadata={"memory": 1024},
        )
    ]
    terraform = TerraformStateParser().parse(
        {
            "resources": [
                {
                    "type": "aws_lambda_function",
                    "name": "process_order",
                    "instances": [{"attributes": {"function_name": "process-order", "memory_size": 512}}],
                }
            ]
        }
    )
    rows = ReconciliationService().classify(floci, terraform)
    assert rows[0]["status"] == DIFFERENT_CONFIGURATION
    assert rows[0]["differences"][0]["floci"] == 1024
