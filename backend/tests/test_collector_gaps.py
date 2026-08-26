from botocore.exceptions import ClientError

from app.collectors.support import is_expected_collector_gap


def test_unsupported_operation_is_expected() -> None:
    exc = ClientError(
        {"Error": {"Code": "UnsupportedOperation", "Message": "ListDashboards is not supported"}},
        "ListDashboards",
    )
    assert is_expected_collector_gap(exc)


def test_missing_vector_bucket_is_expected() -> None:
    exc = ClientError(
        {
            "Error": {
                "Code": "NotFoundException",
                "Message": "The vector bucket null does not exist.",
            }
        },
        "ListIndexes",
    )
    assert is_expected_collector_gap(exc)
