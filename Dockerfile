FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m grpc_tools.protoc -I./protobufs --python_out=. --grpc_python_out=. ./protobufs/weather.proto

WORKDIR /app

EXPOSE 50051

CMD ["python", "-m", "server.weather_server"]