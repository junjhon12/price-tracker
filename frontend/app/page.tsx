"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { TrackedItem } from "@/lib/api";
import { AddItemForm } from "@/components/AddItemForm";
import { ItemCard } from "@/components/ItemCard";

export default function Home() {
  const [items, setItems] = useState<TrackedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshingAll, setRefreshingAll] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadItems = useCallback(async () => {
    try {
      const data = await api.listItems();
      setItems(data);
    } catch (e) {
      setError("Could not reach the backend at " + (process.env.NEXT_PUBLIC_BACKEND_URL ?? "https://price-tracker-api-gamma.vercel.app"));
      console.error("listItems failed:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  function handleAdded(item: TrackedItem) {
    setItems((prev) => {
      const exists = prev.find((i) => i.id === item.id);
      if (exists) return prev.map((i) => (i.id === item.id ? item : i));
      return [item, ...prev];
    });
  }

  function handleRefreshed(id: number, price: number | null, error: string | null) {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              latest_price: price,
              latest_error: error,
              latest_scraped_at: new Date().toISOString(),
            }
          : item
      )
    );
  }

  async function handleRefreshAll() {
    setRefreshingAll(true);
    try {
      const results = await api.refreshAll();
      setItems((prev) =>
        prev.map((item) => {
          const r = results.find((x) => x.id === item.id);
          if (!r) return item;
          return {
            ...item,
            latest_price: r.price,
            latest_error: r.error,
            latest_scraped_at: new Date().toISOString(),
          };
        })
      );
    } catch (e) {
      console.error("refreshAll failed:", e);
    } finally {
      setRefreshingAll(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📈</span>
            <h1 className="text-xl font-bold text-gray-900">Price Tracker</h1>
          </div>
          {items.length > 0 && (
            <button
              onClick={handleRefreshAll}
              disabled={refreshingAll}
              className="px-4 py-2 text-sm font-medium bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              {refreshingAll ? "Refreshing…" : "↻ Refresh All"}
            </button>
          )}
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {/* Add form */}
        <section className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Track a new product
          </h2>
          <AddItemForm onAdded={handleAdded} />
        </section>

        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* Item list */}
        <section>
          {loading ? (
            <div className="flex items-center justify-center py-16 text-gray-400">
              <div className="text-center space-y-2">
                <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-sm">Connecting to backend…</p>
              </div>
            </div>
          ) : items.length === 0 && !error ? (
            <div className="text-center py-16 text-gray-400">
              <p className="text-4xl mb-3">🛒</p>
              <p className="font-medium text-gray-600">No items tracked yet</p>
              <p className="text-sm mt-1">
                Paste a product URL above to get started.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
                {items.length} item{items.length !== 1 ? "s" : ""} tracked
              </p>
              {items.map((item) => (
                <ItemCard
                  key={item.id}
                  item={item}
                  onRefreshed={handleRefreshed}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
