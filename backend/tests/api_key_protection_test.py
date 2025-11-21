import pytest

from grpc import StatusCode, unary_unary_rpc_method_handler

from security.access import APIKeyInterceptor


@pytest.mark.asyncio
async def test_api_key_interceptor_allows_valid_key():
    api_key = "secret"
    interceptor = APIKeyInterceptor(api_key)

    class HCD:
        def __init__(self, metadata):
            self.invocation_metadata = metadata

    called = False

    async def continuation(details):
        nonlocal called
        called = True
        return "continued"

    hcd = HCD([('x-api-key', 'secret')])
    result = await interceptor.intercept_service(continuation, hcd)

    assert called is True
    assert result == "continued"


@pytest.mark.asyncio
async def test_api_key_interceptor_denies_invalid_key():
    interceptor = APIKeyInterceptor("expected")

    class HCD:
        def __init__(self, metadata):
            self.invocation_metadata = metadata

    async def continuation(details):
        return "won't be used"

    hcd = HCD([])  
    result = await interceptor.intercept_service(continuation, hcd)

    assert hasattr(result, "unary_unary")
    assert callable(result.unary_unary)
