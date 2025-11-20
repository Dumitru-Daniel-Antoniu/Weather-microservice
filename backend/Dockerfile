FROM python:3.11

WORKDIR /app

COPY backend/ /app
COPY protobufs/ /app/protobufs/
COPY core/ /app/core/
COPY .env /app/.env
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m grpc_tools.protoc -I./protobufs --python_out=. --grpc_python_out=. ./protobufs/weather.proto

EXPOSE 50051

CMD ["python", "-m", "server.weather_server"]