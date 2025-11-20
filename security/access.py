import grpc

from grpc import StatusCode
from grpc.aio import ServerInterceptor


class APIKeyInterceptor(ServerInterceptor):
    "Validate the x-api-key metadata in incoming gRPC requests."

    def __init__(self, api_key):
        self.api_key = api_key


    async def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)

        api_key = metadata.get('x-api-key')
        if api_key != self.api_key:
            context = grpc.ServicerContext()
            context.abort(StatusCode.UNAUTHENTICATED, "Invalid or missing API key")

        return await continuation(handler_call_details)
