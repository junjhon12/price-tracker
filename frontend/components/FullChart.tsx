"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { PricePoint } from "@/lib/api";

interface Props {
  history: PricePoint[];
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function FullChart({ history }: Props) {
  const data = history
    .filter((p) => p.price !== null)
    .map((p) => ({ price: p.price, label: fmt(p.scraped_at) }));

  if (data.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic py-4">
        No price data to display yet.
      </p>
    );
  }

  const prices = data.map((d) => d.price as number);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const pad = (max - min) * 0.1 || 1;

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 11 }}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          domain={[min - pad, max + pad]}
          tick={{ fontSize: 11 }}
          tickFormatter={(v: number) => `$${v.toFixed(0)}`}
          tickLine={false}
          axisLine={false}
          width={52}
        />
        <Tooltip formatter={(v) => (typeof v === "number" ? [`$${v.toFixed(2)}`, "Price"] : [String(v), "Price"])} />
        <Line
          type="monotone"
          dataKey="price"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 4, fill: "#3b82f6" }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
