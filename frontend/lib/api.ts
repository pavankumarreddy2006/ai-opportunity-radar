import { fallbackSignals, fallbackTrending, fallbackWeeklyReport } from "@/lib/fallback-data";
import { DashboardResponse, PreferenceResponse, Signal, TrendingGroup, WeeklyReport } from "@/lib/types";

const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_URL = rawApiBaseUrl.startsWith("http") ? rawApiBaseUrl : `https://${rawApiBaseUrl}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    let response: Response | null = null;
    let lastError: unknown = null;
    for (let attempt = 0; attempt < 2; attempt += 1) {
      try {
        response = await fetch(`${API_BASE_URL}${path}`, {
          ...init,
          headers: {
            "Content-Type": "application/json",
            ...(init?.headers ?? {}),
          },
          signal: controller.signal,
          next: { revalidate: init?.method && init.method !== "GET" ? 0 : 180 },
        });
        if (response.ok || response.status < 500) {
          break;
        }
      } catch (error) {
        lastError = error;
        if (attempt === 1) {
          throw error;
        }
      }
    }

    if (!response) {
      throw lastError instanceof Error ? lastError : new Error("API request failed");
    }

    if (!response.ok) {
      console.error(`API request failed with status ${response.status} for path: ${path}`);
      throw new Error(`API request failed with status ${response.status}`);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    console.error(`API request error for ${path}:`, error);
    throw error;
  } finally {
    clearTimeout(timeout);
  }
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
    console.error("Failed to save preferences:", error);
    throw new Error("Failed to save preferences. Please try again.");
  }
}
