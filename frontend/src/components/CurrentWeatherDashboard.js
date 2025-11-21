import React, { useState } from "react";

function CurrentWeatherDashboard() {
  const [city, setCity] = useState("");
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState("");

  const handleExtract = async () => {
    setError("");
    setWeather(null);
    if (!city) {
      setError("Please enter a city.");
      return;
    }
    try {
      const response = await fetch(
        `http://localhost:8000/api/weather?city=${encodeURIComponent(city)}`
      );
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        setWeather(null);
      } else if (data.weather_description && data.weather_description.toLowerCase().includes("error")) {
        setError(data.weather_description);
        setWeather(null);
      } else {
        setWeather(data);
      }
    } catch (err) {
      setError("Failed to fetch weather data.");
      setWeather(null);
    }
  };

  return (
    <div style={{
      maxWidth: 1000,
      width: "100%",
      margin: "40px auto",
      padding: 32,
      background: "#fff",
      borderRadius: 20,
      boxShadow: "0 2px 16px #0001"
    }}>
      <h2 style={{
        textAlign: "center",
        margin: "40px 0 24px 0",
        color: "#22577A",
        fontSize: 32,
        fontWeight: 700,
        letterSpacing: 1
      }}>
        Weather Data Extractor
      </h2>
      <div style={{ display: "flex", gap: 12, marginBottom: 24, justifyContent: "center" }}>
        <input
          value={city}
          onChange={e => setCity(e.target.value)}
          placeholder="Enter a city"
          style={{ width: 220, padding: 10, borderRadius: 8, border: "1px solid #ccc", fontSize: 18 }}
        />
        <button
          onClick={handleExtract}
          style={{ padding: "10px 28px", borderRadius: 8, background: "#2563eb", color: "#fff", border: "none", cursor: "pointer", fontSize: 18 }}
        >
          Extract
        </button>
      </div>
      {error && (
        <div style={{
          background: "#fee2e2",
          color: "#b91c1c",
          border: "1px solid #fca5a5",
          borderRadius: 12,
          padding: "14px 20px",
          margin: "0 auto 16px auto",
          maxWidth: 500,
          textAlign: "center",
          fontWeight: 600,
          fontSize: 18,
          boxShadow: "0 2px 8px #fca5a555"
        }}>
          {error}
        </div>
      )}
      {weather && (
        <div style={{ display: "flex", justifyContent: "center" }}>
          <table style={{
            borderCollapse: "separate",
            borderSpacing: 0,
            width: "96%",
            minWidth: 900,
            fontSize: 20,
            background: "#f3f4f6",
            borderRadius: 12,
            boxShadow: "0 2px 8px #0001",
            overflow: "hidden"
          }}>
            <tbody>
              <tr style={{ background: "#c7d2fe" }}>
                <td style={{ fontWeight: 700, padding: "12px 24px", borderBottom: "1px solid #ddd" }}>Temperature</td>
                <td style={{ padding: "12px 24px", borderBottom: "1px solid #ddd" }}>{weather.temperature} °C</td>
              </tr>
              <tr style={{ background: "#e0e7ff" }}>
                <td style={{ fontWeight: 700, padding: "12px 24px", borderBottom: "1px solid #ddd" }}>Weather</td>
                <td style={{ padding: "12px 24px", borderBottom: "1px solid #ddd" }}>{weather.weather_description}</td>
              </tr>
              <tr style={{ background: "#c7d2fe" }}>
                <td style={{ fontWeight: 700, padding: "12px 24px", borderBottom: "1px solid #ddd" }}>Humidity</td>
                <td style={{ padding: "12px 24px", borderBottom: "1px solid #ddd" }}>{weather.humidity} %</td>
              </tr>
              <tr style={{ background: "#e0e7ff" }}>
                <td style={{ fontWeight: 700, padding: "12px 24px" }}>Wind Speed</td>
                <td style={{ padding: "12px 24px" }}>{weather.wind_speed} m/s</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default CurrentWeatherDashboard;