"use client";

import { useState } from "react";
import Image from "next/image";
import type { TrackedItem, PricePoint } from "@/lib/api";
import { api } from "@/lib/api";
import { SparklineChart } from "./SparklineChart";
import { FullChart } from "./FullChart";

interface Props {
  item: TrackedItem;
  onRefreshed: (id: number, price: number | null, error: string | null) => void;
}

export function ItemCard({ item, onRefreshed }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [history, setHistory] = useState<PricePoint[] | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function toggleExpand() {
    if (!expanded && !history) {
      setLoadingHistory(true);
      try {
        const data = await api.getHistory(item.id);
        setHistory(data.history);
      } catch (e) {
        console.error("getHistory failed:", e);
      } finally {
        setLoadingHistory(false);
      }
    }
    setExpanded((v) => !v);
  }

  async function handleRefresh(e: React.MouseEvent) {
    e.stopPropagation();
    setRefreshing(true);
    try {
      const result = await api.refreshItem(item.id);
      onRefreshed(item.id, result.price, result.error);
      // Reload history if panel is open
      if (expanded) {
        const data = await api.getHistory(item.id);
        setHistory(data.history);
      } else {
        setHistory(null); // force reload on next expand
      }
    } catch (e) {
      console.error("refreshItem failed:", e);
    } finally {
      setRefreshing(false);
    }
  }

  const priceLabel =
    item.latest_price !== null
      ? `$${item.latest_price.toFixed(2)}`
      : item.latest_error
      ? "Error"
      : "—";

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      {/* Header row */}
      <div
        className="flex items-center gap-4 p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={toggleExpand}
      >
        {/* Product image */}
        <div className="flex-shrink-0 w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
          {item.image_url ? (
            <Image
              src={item.image_url}
              alt={item.title ?? "product"}
              width={64}
              height={64}
              className="w-full h-full object-contain"
              unoptimized
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300 text-2xl">
              🛒
            </div>
          )}
        </div>

        {/* Title + URL */}
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 truncate">
            {item.title ?? new URL(item.url).hostname}
          </p>
          <p className="text-xs text-gray-400 truncate">{item.url}</p>
          {item.latest_error && (
            <p className="text-xs text-red-500 truncate mt-0.5">
              {item.latest_error}
            </p>
          )}
        </div>

        {/* Sparkline */}
        <div className="hidden sm:block flex-shrink-0">
          {history && history.length > 0 ? (
            <SparklineChart history={history} />
          ) : (
            <div className="w-[120px] h-[40px]" />
          )}
        </div>

        {/* Price */}
        <div className="flex-shrink-0 text-right">
          <span
            className={`text-lg font-bold ${
              item.latest_error ? "text-red-500" : "text-blue-600"
            }`}
          >
            {priceLabel}
          </span>
          {item.latest_scraped_at && (
            <p className="text-xs text-gray-400 mt-0.5">
              {new Date(item.latest_scraped_at).toLocaleTimeString(undefined, {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          )}
        </div>

        {/* Refresh button */}
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex-shrink-0 px-3 py-1.5 text-sm font-medium rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50 transition-colors"
        >
          {refreshing ? "…" : "↻"}
        </button>

        {/* Expand chevron */}
        <span className="flex-shrink-0 text-gray-400 text-sm">
          {expanded ? "▲" : "▼"}
        </span>
      </div>

      {/* Expanded chart */}
      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-gray-100">
          {loadingHistory ? (
            <div className="flex items-center justify-center py-8 text-gray-400 text-sm">
              Loading history…
            </div>
          ) : (
            <div className="mt-4">
              <FullChart history={history ?? []} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
