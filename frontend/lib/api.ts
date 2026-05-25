import { fallbackSignals, fallbackTrending, fallbackWeeklyReport } from "@/lib/fallback-data";
import { DashboardResponse, PreferenceResponse, Signal, TrendingGroup, WeeklyReport } from "@/lib/types";

const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_URL = rawApiBaseUrl.startsWith("http") ? rawApiBaseUrl : `https://${rawApiBaseUrl}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let lastError: unknown = null;
  const attempts = init?.method && init.method !== "GET" ? 1 : 3;

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(init?.headers ?? {}),
        },
        signal: controller.signal,
        next: { revalidate: init?.method && init.method !== "GET" ? 0 : 120 },
      });

      if (!response.ok) {
        lastError = new Error(`API request failed with status ${response.status}`);
        if (response.status >= 500 && attempt < attempts - 1) {
          await delay(350 * (attempt + 1));
          continue;
        }
        throw lastError;
      }

      return parseJson<T>(response);
    } catch (error) {
      lastError = error;
      if (attempt < attempts - 1) {
        await delay(350 * (attempt + 1));
        continue;
      }
    } finally {
      clearTimeout(timeout);
    }
  }

  throw lastError instanceof Error ? lastError : new Error("API request failed");
}

export async function getSignals(email?: string): Promise<Signal[]> {
  const query = email ? `?email=${encodeURIComponent(email)}&limit=24` : "?limit=24";
  try {
    const signals = await request<Signal[]>(`/news${query}`);
    return signals && signals.length > 0 ? signals : fallbackSignals;
  } catch (error) {
    console.warn("Failed to load signals, using fallback data");
    return fallbackSignals;
  }
}

export async function getTrending(): Promise<TrendingGroup[]> {
  try {
    const trending = await request<TrendingGroup[]>("/trending");
    return trending && trending.some((group) => group.signals.length > 0) ? trending : fallbackTrending;
  } catch (error) {
    console.warn("Failed to load trending, using fallback data");
    return fallbackTrending;
  }
}

export async function getDashboard(email?: string): Promise<DashboardResponse> {
  const query = email ? `?email=${encodeURIComponent(email)}` : "";
  try {
    const dashboard = await request<DashboardResponse>(`/dashboard${query}`);
    return dashboard && dashboard.top_signals.length > 0
      ? dashboard
      : { top_signals: fallbackSignals, trending: fallbackTrending, interests: ["AI", "Coding", "Startups"] };
  } catch (error) {
    console.warn("Failed to load dashboard, using fallback data");
    return { top_signals: fallbackSignals, trending: fallbackTrending, interests: ["AI", "Coding", "Startups"] };
  }
}

export async function getWeeklyReport(email?: string): Promise<WeeklyReport> {
  const query = email ? `?email=${encodeURIComponent(email)}` : "";
  try {
    const report = await request<WeeklyReport>(`/weekly-report${query}`);
    return report && report.signals.length > 0 ? report : fallbackWeeklyReport;
  } catch (error) {
    console.warn("Failed to load weekly report, using fallback data");
    return fallbackWeeklyReport;
  }
}

export async function getPreferences(email: string): Promise<PreferenceResponse | null> {
  try {
    return await request<PreferenceResponse>(`/preferences?email=${encodeURIComponent(email)}`);
  } catch (error) {
    console.warn("Failed to load preferences");
    return null;
  }
}

export async function savePreferences(payload: {
  email: string;
  name?: string;
  interests: string[];
}): Promise<PreferenceResponse> {
  try {
    return await request<PreferenceResponse>("/preferences", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw new Error("Failed to save preferences. Please try again.");
  }
}

export async function trackInteraction(payload: {
  email: string;
  signal_id: number;
  action: "click" | "save" | "like" | "view" | "share" | "search";
  category?: string;
  topics?: string[];
  query?: string;
  reading_seconds?: number;
}): Promise<{ status: string }> {
  try {
    return await request<{ status: string }>("/preferences/interaction", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch {
    return { status: "local-only" };
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    return null as T;
  }
  try {
    return JSON.parse(text) as T;
  } catch (error) {
    throw new Error(`Invalid JSON response: ${error instanceof Error ? error.message : "parse failed"}`);
  }
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
