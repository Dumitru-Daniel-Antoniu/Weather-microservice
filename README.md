# SkyScope Weather Viewer — Weather Microservice

---

A client-server weather application that fetches current weather from a public API, serves it over gRPC, stores results in MongoDB and provides a frontend to visualize current and historical data.

- The client is a CLI that asks for a city and calls the gRPC server.
- The server calls the external Weather API, processes the response, stores a document in MongoDB and returns the current weather.
- The frontend (React) calls an HTTP proxy -> backend to get current weather or historical data, then renders 3 charts (temperature, humidity, wind).

---

## Why this project

- Demonstrates gRPC server/client, a microservice-style HTTP proxy, MongoDB persistence, and a React frontend for visualization.  
- Simple, testable components with a clear separation of responsibilities.

---

## Core flow

1. Client CLI (gRPC client) submits CityRequest to the gRPC server.  
2. Server receives request, calls external Weather API, processes response.  
3. Server writes the weather document to MongoDB and returns CityWeatherDataResponse to client.  
4. Frontend requests current or historical data via HTTP endpoints exposed by the proxy; the proxy forwards to backend gRPC endpoints and returns JSON for the UI.  
5. History requests return documents in the requested time window and the frontend renders charts.

---

## Technologies

- Python 3.13.9  
- gRPC (protobufs) — service and messages defined in protobufs/weather.proto  
- motor (AsyncIO MongoDB client) for async DB access  
- httpx for external HTTP requests  
- React for the frontend  
- Docker (Dockerfile) for container builds

---

## Project layout

- protobufs/weather.proto — gRPC definitions (CityRequest, CityWeatherDataResponse, HistoryRequest, HistoryResponse, HistoryEntry)  
- backend/ — gRPC server, services, repository and business logic
  - server/weather_server.py — gRPC service implementation
  - client/client.py - CLI client for weather data request
  - repository/weather_repository.py — DB access (insert and history)
  - security/access.py - sets the verification of the x-api-key in the request metadata
  - service/* — processing and persistence helpers
  - db/session.py — MongoDB async motor client
  - tests/* - unit and integration tests for the backend
  - utils/exception_handler.py - maps the exceptions to codes and descriptions to be sent through gRPC
- proxy/ — HTTP proxy exposing /api/weather and /api/history (used by frontend)  
- frontend/ — React UI that calls proxy endpoints  
- core/config.py — configuration of environment variables

---

## gRPC (proto) summary

- weather.proto defines:  
  - RPC Weather(CityRequest) -> CityWeatherDataResponse  
  - RPC WeatherHistory(HistoryRequest) -> HistoryResponse  
- The server implements Weather and WeatherHistory; the protobuf files are compiled with grpc_tools.protoc to generate the Python stubs.

---

## HTTP proxy routes (used by the frontend)

- GET /api/weather?city=<city>  
  - Returns current weather JSON:  
    { city_name, temperature, weather_description, humidity, wind_speed }  

- GET /api/history?city=<city>&start_date=<YYYY-MM-DD HH:MM:SS>&end_date=<YYYY-MM-DD HH:MM:SS>  
  - Returns history JSON:  
    { entries: [ { date, temperature, humidity, wind_speed }, ... ], error: "" }

---

## Quick start

1. Clone the repository
   - git clone https://github.com/Dumitru-Daniel-Antoniu/Weather-microservice.git
2. Go to the root of the project
   - cd Weather-microservice
3. Start the containers
   - docker-compose up --build
4. Access the frontend
   - access in the browser http://localhost:3000
5. Run the client CLI
   - docker exec -it weather_backend python -m client.client in the root of the project

---
