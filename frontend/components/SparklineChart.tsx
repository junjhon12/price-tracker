"use client";

import { LineChart, Line, ResponsiveContainer, Tooltip } from "recharts";
import type { PricePoint } from "@/lib/api";

interface Props {
  history: PricePoint[];
}

export function SparklineChart({ history }: Props) {
  const data = history
    .filter((p) => p.price !== null)
    .map((p) => ({ price: p.price, t: p.scraped_at }));

  if (data.length < 2) {
    return (
      <span className="text-xs text-gray-400 italic">not enough data</span>
    );
  }

  return (
    <ResponsiveContainer width={120} height={40}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey="price"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
        />
        <Tooltip
          formatter={(v) => (typeof v === "number" ? [`$${v.toFixed(2)}`, "price"] : [String(v), "price"])}
          labelFormatter={() => ""}
          contentStyle={{ fontSize: 11, padding: "2px 6px" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
