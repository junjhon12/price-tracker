"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { TrackedItem } from "@/lib/api";

interface Props {
  onAdded: (item: TrackedItem) => void;
}

export function AddItemForm({ onAdded }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;
    setError(null);
    setLoading(true);
    try {
      const item = await api.addItem(url.trim());
      onAdded(item);
      setUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add item");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Paste a product URL…"
        required
        disabled={loading}
        className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:opacity-60 bg-white"
      />
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors text-sm whitespace-nowrap"
      >
        {loading ? "Scraping…" : "Track"}
      </button>
      {error && (
        <p className="text-xs text-red-500 mt-1 sm:hidden">{error}</p>
      )}
    </form>
  );
}
