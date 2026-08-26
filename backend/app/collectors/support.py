from botocore.exceptions import BotoCoreError, ClientError, UnknownServiceError

EXPECTED_ERROR_CODES = {
    "InternalFailure",
    "InvalidAction",
    "NotImplemented",
    "UnknownOperationException",
    "UnsupportedOperation",
    "OptInRequired",
    "NotFoundException",
    "ResourceNotFoundException",
    "InvalidParameterException",
    "InvalidParameterValue",
    "ValidationException",
    "SerializationException",
    "AccessDeniedException",
    "UnrecognizedClientException",
}

EXPECTED_MESSAGE_FRAGMENTS = (
    "not yet implemented",
    "unknown operation",
    "not supported",
    "unsupportedoperation",
    "does not exist",
    "not found",
    "could not connect to the endpoint url",
)


def is_unsupported_api(exc: ClientError) -> bool:
    return is_expected_collector_gap(exc)


def is_expected_collector_gap(exc: BaseException) -> bool:
    if isinstance(exc, UnknownServiceError):
        return True
    code = ""
    if isinstance(exc, ClientError):
        code = str((exc.response or {}).get("Error", {}).get("Code", ""))
    message = str(exc).lower()
    if code in EXPECTED_ERROR_CODES:
        return True
    return any(fragment in message for fragment in EXPECTED_MESSAGE_FRAGMENTS)
