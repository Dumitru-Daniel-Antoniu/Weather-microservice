import grpc
import httpx


def handle_weather_exception(context, e, request_city=None):
    """Maps exceptions to gRPC status codes and messages."""

    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            context.set_details("Invalid API key.")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        elif status == 404:
            context.set_details(f"City '{request_city}' not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
        elif status == 429:
            context.set_details("API rate limit eeeded.")
            context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
        elif status >= 500:
            context.set_details("Weather API server error.")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
        else:
            context.set_details(f"HTTP error occurred: {str(e)}")
            context.set_code(grpc.StatusCode.UNKNOWN)

    elif isinstance(e, httpx.RequestError):
        context.set_details(f"HTTP request error: {str(e)}")
        context.set_code(grpc.StatusCode.UNAVAILABLE)

    elif isinstance(e, ValueError):
        context.set_details("Invalid or malformed response from weather API.")
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)

    elif isinstance(e, RuntimeError):
        context.set_details(f"Runtime error occured: {str(e)}")
        context.set_code(grpc.StatusCode.INTERNAL)

    else:
        context.set_details(f"An unexpected error occurred: {str(e)}")
        context.set_code(grpc.StatusCode.UNKNOWN)
