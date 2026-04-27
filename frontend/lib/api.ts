const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "https://price-tracker-api-gamma.vercel.app";

export interface TrackedItem {
  id: number;
  url: string;
  title: string | null;
  image_url: string | null;
  created_at: string;
  latest_price: number | null;
  latest_scraped_at: string | null;
  latest_error: string | null;
}

export interface PricePoint {
  price: number | null;
  error: string | null;
  scraped_at: string;
}

export interface ItemHistory {
  item: TrackedItem;
  history: PricePoint[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  addItem: (url: string) =>
    request<TrackedItem>("/items", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  listItems: () => request<TrackedItem[]>("/items"),

  getHistory: (id: number) => request<ItemHistory>(`/items/${id}/history`),

  refreshItem: (id: number) =>
    request<{ id: number; price: number | null; error: string | null }>(
      `/items/${id}/refresh`,
      { method: "POST" }
    ),

  refreshAll: () =>
    request<{ id: number; price: number | null; error: string | null }[]>(
      "/refresh-all",
      { method: "POST" }
    ),
};
