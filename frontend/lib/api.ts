import { fallbackSignals, fallbackTrending, fallbackWeeklyReport } from "@/lib/fallback-data";
import { DashboardResponse, PreferenceResponse, Signal, TrendingGroup, WeeklyReport } from "@/lib/types";

const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_URL = rawApiBaseUrl.startsWith("http") ? rawApiBaseUrl : `https://${rawApiBaseUrl}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    next: { revalidate: 3600 },
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getSignals(email?: string): Promise<Signal[]> {
  const query = email ? `?email=${encodeURIComponent(email)}&limit=5` : "?limit=5";
  try {
    const signals = await request<Signal[]>(`/signals${query}`);
    return signals.length > 0 ? signals : fallbackSignals;
  } catch {
    return fallbackSignals;
  }
}

export async function getTrending(): Promise<TrendingGroup[]> {
  try {
    const trending = await request<TrendingGroup[]>("/trending");
    return trending.some((group) => group.signals.length > 0) ? trending : fallbackTrending;
  } catch {
    return fallbackTrending;
  }
}

export async function getDashboard(email?: string): Promise<DashboardResponse> {
  const query = email ? `?email=${encodeURIComponent(email)}` : "";
  try {
    const dashboard = await request<DashboardResponse>(`/dashboard${query}`);
    return dashboard.top_signals.length > 0
      ? dashboard
      : { top_signals: fallbackSignals, trending: fallbackTrending, interests: ["AI", "Coding", "Startups"] };
  } catch {
    return { top_signals: fallbackSignals, trending: fallbackTrending, interests: ["AI", "Coding", "Startups"] };
  }
}

export async function getWeeklyReport(email?: string): Promise<WeeklyReport> {
  const query = email ? `?email=${encodeURIComponent(email)}` : "";
  try {
    const report = await request<WeeklyReport>(`/weekly-report${query}`);
    return report.signals.length > 0 ? report : fallbackWeeklyReport;
  } catch {
    return fallbackWeeklyReport;
  }
}

export async function getPreferences(email: string): Promise<PreferenceResponse | null> {
  try {
    return await request<PreferenceResponse>(`/preferences?email=${encodeURIComponent(email)}`);
  } catch {
    return null;
  }
}

export async function savePreferences(payload: {
  email: string;
  name?: string;
  interests: string[];
}): Promise<PreferenceResponse> {
  return request<PreferenceResponse>("/preferences", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
