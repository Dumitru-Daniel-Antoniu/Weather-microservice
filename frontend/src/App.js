import React, { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const PERIODS = [
  { key: "1h", label: "Last hour" },
  { key: "12h", label: "Last 12 hours" },
  { key: "24h", label: "Last 24 hours" },
  { key: "48h", label: "Last 48 hours" },
  { key: "72h", label: "Last 72 hours" },
  { key: "5d", label: "Last 5 days" }
]

function MetricChart({ data, dataKey, color, title, unit }) {
  return (
    <div style={{ background: "#f3f4f6", borderRadius: 12, padding: 16, marginBottom: 16 }}>
      <h3 style={{ margin: 0, marginBottom: 8 }}>{title}</h3>
      <div style={{ width: "100%", minWidth: 900, height: 220 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`color-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.7} />
              <stop offset="100%" stopColor={color} stopOpacity={0.2} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip formatter={(value) => `${value} ${unit}`} />
          <Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#color-${dataKey})`} />
        </AreaChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}

function getPeriodRange(periodKey) {
  const now = new Date();
  let ms = 0;
  if (periodKey === "1h") ms = 60 * 60 * 1000;
  else if (periodKey === "12h") ms = 12 * 60 * 60 * 1000;
  else if (periodKey === "24h") ms = 24 * 60 * 60 * 1000;
  else if (periodKey === "48h") ms = 48 * 60 * 60 * 1000;
  else if (periodKey === "72h") ms = 72 * 60 * 60 * 1000;
  else if (periodKey === "5d") ms = 5 * 24 * 60 * 60 * 1000;
  const end = now;
  const start = new Date(now.getTime() - ms);
  function pad(n) {
    return n < 10 ? '0' + n : n;
  }
  const formatLocal = d =>
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  return [formatLocal(start), formatLocal(end)];
}

function App() {
  useEffect(() => {
    document.documentElement.style.overscrollBehavior = "none";
    document.body.style.overscrollBehavior = "none";
    return () => {
      document.documentElement.style.overscrollBehavior = "";
      document.body.style.overscrollBehavior = "";
    };
  }, []);

  const [city, setCity] = useState("");
  const [temperatureData, setTemperatureData] = useState([]);
  const [humidityData, setHumidityData] = useState([]);
  const [windData, setWindData] = useState([]);
  const [period, setPeriod] = useState(PERIODS[0].key);
  const [showDropdown, setShowDropdown] = useState(false);
  const [error, setError] = useState("");
  const [showCharts, setShowCharts] = useState(false);

  const handleGenerate = async () => {
    setError("");
    setTemperatureData([]);
    setHumidityData([]);
    setWindData([]);
    setShowCharts(false);
    const [start_date, end_date] = getPeriodRange(period);
    try {
      const response = await fetch(
        `http://localhost:8000/api/history?city=${encodeURIComponent(city)}&start_date=${encodeURIComponent(start_date)}&end_date=${encodeURIComponent(end_date)}`
      );
      const response_json = await response.json();
      if (response_json.error) {
        setError(response_json.error);
        setTemperatureData([]);
        setHumidityData([]);
        setWindData([]);
        setShowCharts(false);
      } else if (!response_json.entries || response_json.entries.length === 0) {
        setError("No data found for this city and period.");
        setTemperatureData([]);
        setHumidityData([]);
        setWindData([]);
        setShowCharts(false);
      } else {
        setTemperatureData(response_json.entries.map(e => ({
          time: e.date.slice(11, 16),
          temperature: e.temperature
        })));
        setHumidityData(response_json.entries.map(e => ({
          time: e.date.slice(11, 16),
          humidity: e.humidity
        })));
        setWindData(response_json.entries.map(e => ({
          time: e.date.slice(11, 16),
          wind: e.wind_speed
        })));
        setShowCharts(true);
      }
    }
    catch (err) {
      setError("Failed to fetch data from server.");
      setTemperatureData([]);
      setHumidityData([]);
      setWindData([]);
      setShowCharts(false);
    }
  };  

  const handlePeriodSelect = (key) => {
    setPeriod(key);
    setShowDropdown(false);
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#b3c7e6",
        margin: 0,
        padding: 0,
        paddingBottom: 48,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        overflowX: "hidden"
      }}
    >
      <h1
        style={{
          textAlign: "center",
          margin: 0,
          paddingTop: 40,
          paddingBottom: 24,
          fontSize: 44,
          fontWeight: 800,
          color: "#22577A" 
        }}
      >
        SkyScope Weather Viewer
      </h1>
      <div style={{ maxWidth: 1100, margin: "40px auto", padding: 32, background: "#fff", borderRadius: 20, boxShadow: "0 2px 16px #0001", marginBottom: 0 }}>
        <div style={{ display: "flex", gap: 12, marginBottom: 32, justifyContent: "center" }}>
          <input
            value={city}
            onChange={e => setCity(e.target.value)}
            placeholder="Enter city"
            style={{ width: 220, flex: "none", padding: 10, borderRadius: 8, border: "1px solid #ccc", fontSize: 18 }}
          />
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setShowDropdown((v) => !v)}
              style={{
                padding: "10px 18px",
                borderRadius: 8,
                background: "#f3f4f6",
                border: "1px solid #ccc",
                cursor: "pointer",
                minWidth: 160,
                textAlign: "left",
                fontSize: 18
              }}
            >
              {PERIODS.find(p => p.key === period)?.label}
            </button>
            {showDropdown && (
              <div style={{
                position: "absolute",
                top: "110%",
                left: 0,
                background: "#fff",
                border: "1px solid #ccc",
                borderRadius: 8,
                boxShadow: "0 2px 8px #0002",
                zIndex: 10,
                minWidth: 180
              }}>
                {PERIODS.map(p => (
                  <div
                    key={p.key}
                    onClick={() => handlePeriodSelect(p.key)}
                    style={{
                      padding: "10px 18px",
                      cursor: "pointer",
                      background: p.key === period ? "#e0e7ff" : "transparent"
                    }}
                  >
                    {p.label}
                  </div>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={handleGenerate}
            style={{ padding: "10px 28px", borderRadius: 8, background: "#2563eb", color: "#fff", border: "none", cursor: "pointer", fontSize: 18 }}
          >
            Generate
          </button>
        </div>
        {error && (
          <div style={{ color: "#dc2626", marginBottom: 24, textAlign: "center", fontSize: 18 }}>
            {error}
          </div>
        )}
        {showCharts && (
          <>
            <MetricChart data={temperatureData} dataKey="temperature" color="#38bdae" areaTop="#38bdae" areaBottom="#a8ffeb" title="Temperature (°C)" unit="°C" />
            <MetricChart data={humidityData} dataKey="humidity" color="#38bdf8" areaTop="#bae6fd" areaBottom="#38bdf8" title="Humidity (%)" unit="%" />
            <MetricChart data={windData} dataKey="wind" color="#64748b" areaTop="#cbd5e1" areaBottom="#64748b" title="Wind Speed (m/s)" unit="m/s" />
          </>
        )}
      </div>
    </div>
  );
}

export default App;