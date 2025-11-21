import React, { useState, useEffect } from "react";
import CurrentWeatherDashboard from "./components/CurrentWeatherDashboard";
import HistoryDashboard from "./components/HistoryDashboard";

const PERIODS = [
  { key: "1h", label: "Last hour" },
  { key: "12h", label: "Last 12 hours" },
  { key: "24h", label: "Last 24 hours" },
  { key: "48h", label: "Last 48 hours" },
  { key: "72h", label: "Last 72 hours" },
  { key: "5d", label: "Last 5 days" }
];

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

  const [timeToDateMap, setTimeToDateMap] = useState({});
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
      if (!city) {
        setError("Please enter a city.");
        return;
      }
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
          temperature: e.temperature,
          date: e.date
        })));
        setHumidityData(response_json.entries.map(e => ({
          time: e.date.slice(11, 16),
          humidity: e.humidity,
          date: e.date
        })));
        setWindData(response_json.entries.map(e => ({
          time: e.date.slice(11, 16),
          wind: e.wind_speed,
          date: e.date
        })));
        setShowCharts(true);
      }
      const timeToDateMap = {};
      response_json.entries.forEach(e => {
        timeToDateMap[e.date.slice(11, 16)] = e.date.slice(0, 10); //
      });
      setTimeToDateMap(timeToDateMap);
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
      <CurrentWeatherDashboard />
      <HistoryDashboard
        city={city}
        setCity={setCity}
        period={period}
        setPeriod={setPeriod}
        PERIODS={PERIODS}
        showDropdown={showDropdown}
        setShowDropdown={setShowDropdown}
        handleGenerate={handleGenerate}
        error={error}
        showCharts={showCharts}
        temperatureData={temperatureData}
        humidityData={humidityData}
        windData={windData}
        timeToDateMap={timeToDateMap}
      />
    </div>
  );
}

export default App;