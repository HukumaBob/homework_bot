class ValuesMissingError(Exception):
    """Token or other values missed."""


class CheckResponseError(Exception):
    """Check API and documentation correspondence."""


class GetApiAnswerError(Exception):
    """Check API - endpoint correspondence."""
