from types import SimpleNamespace
from unittest.mock import MagicMock

from app.collectors.generic import GENERIC_SPECS, GenericListCollector, ListSpec, build_generic_collectors
from app.collectors.registry import COLLECTORS
from app.floci.client import FlociClient


def test_floci_matrix_collectors_are_registered() -> None:
    assert len(COLLECTORS) >= 75
    for spec in GENERIC_SPECS:
        assert spec.name in COLLECTORS


def test_generic_list_collector_normalizes_items() -> None:
    spec = ListSpec("rds", "RDS", "rds", "describe_db_instances", "DBInstances", "db_instance", "DBInstanceIdentifier", "DBInstanceIdentifier")

    class Built(GenericListCollector):
        service_name = "rds"

        def __init__(self, client):
            super().__init__(client)
            self.spec = spec

    fake = MagicMock()
    fake.meta = SimpleNamespace(region_name="us-east-1")
    fake.get_paginator.side_effect = RuntimeError("none")
    fake.describe_db_instances.return_value = {
        "DBInstances": [{"DBInstanceIdentifier": "orders-db", "DBInstanceStatus": "available"}]
    }
    floci = MagicMock(spec=FlociClient)
    floci.get_client.return_value = fake
    resources = Built(floci).collect_sync()
    assert resources[0].id == "rds:orders-db"
    assert resources[0].service == "rds"
