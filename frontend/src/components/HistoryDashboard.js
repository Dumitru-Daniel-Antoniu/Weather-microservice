import React from "react";
import MetricChart from "./MetricChart";

function HistoryDashboard({
  city, setCity, period, setPeriod, PERIODS,
  showDropdown, setShowDropdown,
  handleGenerate, error, showCharts,
  temperatureData, humidityData, windData, timeToDateMap
}) {
  const handlePeriodSelect = (key) => {
    setPeriod(key);
    setShowDropdown(false);
  };

  return (
    <div style={{ maxWidth: 1000, width: "100%", margin: "40px auto", padding: 32, background: "#fff", borderRadius: 20, boxShadow: "0 2px 16px #0001", marginBottom: 0 }}>
        <h2 style={{
            textAlign: "center",
            margin: "40px 0 24px 0",
            color: "#22577A",
            fontSize: 32,
            fontWeight: 700,
            letterSpacing: 1
        }}>
            Temperature, Humidity and Wind Speed Status
        </h2>
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
        {showCharts && (
            <>
            <MetricChart data={temperatureData} dataKey="temperature" color="#38bdae" areaTop="#38bdae" areaBottom="#a8ffeb" title="Temperature (°C)" unit="°C" timeToDateMap={timeToDateMap} />
            <MetricChart data={humidityData} dataKey="humidity" color="#38bdf8" areaTop="#bae6fd" areaBottom="#38bdf8" title="Humidity (%)" unit="%" timeToDateMap={timeToDateMap} />
            <MetricChart data={windData} dataKey="wind" color="#64748b" areaTop="#cbd5e1" areaBottom="#64748b" title="Wind Speed (m/s)" unit="m/s" timeToDateMap={timeToDateMap} />
            </>
        )}
        </div>
  );
}

export default HistoryDashboard;