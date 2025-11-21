import React from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function CustomTick({ x, y, payload, timeToDateMap }) {
  const time = payload.value;
  let dateStr = "";
  const date = timeToDateMap ? timeToDateMap[time] : undefined;
  if (date) {
    const [year, month, day] = date.split("-");
    dateStr = `${month}/${day}`;
  }
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={18} textAnchor="middle" fill="#504f4fff" fontSize={16}>
        {time}
      </text>
      <text x={0} y={0} dy={36} textAnchor="middle" fill="#504f4fff" fontSize={16}>
        {dateStr}
      </text>
    </g>
  );
}

function CustomTooltip({ active, payload, label, unit, timeToDateMap }) {
  if (active && payload && payload.length) {
    const time = label;
    let dateStr = "";
    if (timeToDateMap && timeToDateMap[time]) {
      const [year, month, day] = timeToDateMap[time].split("-");
      dateStr = `${month}/${day}`;
    }
    return (
      <div style={{
        background: "#fff",
        border: "1px solid #e5e7eb",
        borderRadius: 8,
        padding: "10px 16px",
        boxShadow: "0 2px 8px #0001",
        fontSize: 15,
        color: "#222"
      }}>
        <div style={{ fontWeight: 600, marginBottom: 2 }}>
          {time} <span style={{ color: "#888", fontWeight: 400 }}>({dateStr})</span>
        </div>
        <div>
          <span style={{ textTransform: "capitalize" }}>{payload[0].name}</span>
          {` : `}
          <span style={{ color: "#2563eb", fontWeight: 600 }}>{payload[0].value} {unit}</span>
        </div>
      </div>
    );
  }
  return null;
}

function MetricChart({ data, dataKey, color, title, unit, timeToDateMap }) {
  const tickInterval = data.length > 10 ? Math.ceil(data.length / 10) : 0;
  return (
    <div style={{ background: "#f3f4f6", borderRadius: 12, padding: 16, marginBottom: 16 }}>
      <h3 style={{ margin: 0, marginBottom: 8 }}>{title}</h3>
      <div style={{ width: "100%", minWidth: 900, height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart 
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 50 }}
        >
          <defs>
            <linearGradient id={`color-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.7} />
              <stop offset="100%" stopColor={color} stopOpacity={0.2} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
          <XAxis 
            dataKey="time"
            tick={<CustomTick timeToDateMap={timeToDateMap} />}
            interval={tickInterval}
          />
          <YAxis />
          <Tooltip
            content={
              <CustomTooltip
                unit={unit}
                timeToDateMap={timeToDateMap}
              />
            }
          />
          <Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#color-${dataKey})`} />
        </AreaChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}

export default MetricChart;