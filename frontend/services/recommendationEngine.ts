import { Signal } from "@/lib/types";
import { isLowQuality, scoreNews } from "@/services/newsScoring";

export type FeedTab = "for-you" | "trending" | "latest" | "saved";

export type UserBehavior = {
  clickedIds: number[];
  savedIds: number[];
  likedIds: number[];
  readingTimeById: Record<string, number>;
  searchHistory: string[];
  categoriesViewed: Record<string, number>;
  topicWeights: Record<string, number>;
};

export type RadarProfile = UserBehavior & {
  email: string;
  interests: string[];
  onboarded: boolean;
  lastSyncedAt?: string;
};

export const DEFAULT_EMAIL = "demo@ainewscollector.ai";
export const STORAGE_KEY = "ai-radar-profile-v3";

export const DEFAULT_PROFILE: RadarProfile = {
  email: DEFAULT_EMAIL,
  interests: [],
  likedIds: [],
  savedIds: [],
  clickedIds: [],
  readingTimeById: {},
  searchHistory: [],
  categoriesViewed: {},
  topicWeights: {},
  onboarded: false,
};

export type RecommendationBreakdown = {
  score: number;
  interestMatch: number;
  engagementScore: number;
  clickHistory: number;
  savedPreference: number;
  freshnessScore: number;
  trendingScore: number;
};

export function rankRecommendations(signals: Signal[], profile: RadarProfile) {
  return dedupeSignals(signals)
    .filter((signal) => !isLowQuality(signal))
    .map((signal) => ({ signal, ranking: scoreSignal(signal, profile) }))
    .sort((left, right) => right.ranking.score - left.ranking.score)
    .map((item) => item.signal);
}

export function sortLatest(signals: Signal[]) {
  return dedupeSignals(signals).sort((a, b) => timestamp(b) - timestamp(a));
}

export function sortTrending(signals: Signal[]) {
  return dedupeSignals(signals).sort((a, b) => {
    const left = scoreNews(a).trendScore + a.importance_score + a.opportunity_score * 4;
    const right = scoreNews(b).trendScore + b.importance_score + b.opportunity_score * 4;
    return right - left;
  });
}

export function savedSignals(signals: Signal[], profile: RadarProfile) {
  const saved = new Set(profile.savedIds);
  return dedupeSignals(signals).filter((signal) => saved.has(signal.id));
}

export function filterSignals(signals: Signal[], query: string) {
  const search = normalize(query);
  if (!search) {
    return signals;
  }
  return signals.filter((signal) =>
    normalize(
      [
        signal.raw_title,
        signal.summary?.headline,
        signal.summary?.what_happened,
        signal.summary?.why_it_matters,
        signal.category,
        signal.source,
        ...signal.tags,
      ]
        .filter(Boolean)
        .join(" "),
    ).includes(search),
  );
}

export function scoreSignal(signal: Signal, profile: RadarProfile): RecommendationBreakdown {
  const topics = signalTopics(signal);
  const interests = profile.interests.map(normalize);
  const matchedInterests = topics.filter((topic) =>
    interests.some((interest) => topic.includes(interest) || interest.includes(topic)),
  );
  const topicAffinity = topics.reduce((sum, topic) => sum + (profile.topicWeights[topic] ?? 0), 0);
  const categoryViews = profile.categoriesViewed[normalize(signal.category)] ?? 0;
  const quality = scoreNews(signal);

  const interestMatch = clamp((matchedInterests.length ? 70 : 0) + topicAffinity * 4 + categoryViews * 3, 0, 100);
  const engagementScore = clamp(signal.importance_score * 0.35 + signal.opportunity_score * 5 + quality.qualityScore * 0.2, 0, 100);
  const clickHistory = profile.clickedIds.includes(signal.id) ? 100 : clamp(topicAffinity * 8, 0, 100);
  const savedPreference = profile.savedIds.includes(signal.id) ? 100 : profile.likedIds.includes(signal.id) ? 74 : clamp(topicAffinity * 6, 0, 100);
  const freshness = freshnessScore(signal);
  const trendingScore = clamp(quality.trendScore, 0, 100);

  return {
    interestMatch,
    engagementScore,
    clickHistory,
    savedPreference,
    freshnessScore: freshness,
    trendingScore,
    score:
      interestMatch * 0.35 +
      engagementScore * 0.2 +
      clickHistory * 0.15 +
      savedPreference * 0.15 +
      freshness * 0.1 +
      trendingScore * 0.05,
  };
}

export function recordBehavior(profile: RadarProfile, signal: Signal, action: "like" | "save" | "click" | "view" | "share", readingSeconds = 0): RadarProfile {
  const topicWeights = { ...profile.topicWeights };
  const categoriesViewed = { ...profile.categoriesViewed };
  const readingTimeById = { ...profile.readingTimeById };
  const weight = action === "click" ? 2 : action === "save" || action === "like" ? 3 : 1;

  for (const topic of signalTopics(signal)) {
    topicWeights[topic] = clamp((topicWeights[topic] ?? 0) + weight, 0, 100);
  }

  const category = normalize(signal.category);
  categoriesViewed[category] = (categoriesViewed[category] ?? 0) + 1;

  if (readingSeconds > 0) {
    readingTimeById[String(signal.id)] = (readingTimeById[String(signal.id)] ?? 0) + readingSeconds;
  }

  return {
    ...profile,
    likedIds: action === "like" ? toggleId(profile.likedIds, signal.id) : profile.likedIds,
    savedIds: action === "save" ? toggleId(profile.savedIds, signal.id) : profile.savedIds,
    clickedIds: action === "click" ? unique([...profile.clickedIds, signal.id]).slice(-120) : profile.clickedIds,
    topicWeights,
    categoriesViewed,
    readingTimeById,
  };
}

export function addSearch(profile: RadarProfile, query: string): RadarProfile {
  const normalized = query.trim();
  if (normalized.length < 2) {
    return profile;
  }
  return {
    ...profile,
    searchHistory: unique([normalized, ...profile.searchHistory]).slice(0, 30),
  };
}

export function loadProfile(): RadarProfile {
  if (typeof window === "undefined") {
    return DEFAULT_PROFILE;
  }
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value ? { ...DEFAULT_PROFILE, ...JSON.parse(value) } : DEFAULT_PROFILE;
  } catch {
    return DEFAULT_PROFILE;
  }
}

export function saveProfile(profile: RadarProfile) {
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  }
}

export function signalTopics(signal: Signal) {
  return unique(
    [signal.category, ...signal.tags, ...(signal.summary?.headline ?? "").split(" "), ...(signal.raw_title ?? "").split(" ")]
      .map(normalize)
      .filter((topic) => topic.length > 2),
  );
}

export function dedupeSignals(signals: Signal[]) {
  const seen = new Set<string>();
  const output: Signal[] = [];
  for (const signal of signals) {
    const key = `${normalize(signal.raw_title)}-${normalize(signal.link)}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    output.push(signal);
  }
  return output;
}

export function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function freshnessScore(signal: Signal) {
  const hours = Math.max((Date.now() - timestamp(signal)) / 36e5, 0);
  return clamp(100 - hours * 2.5, 0, 100);
}

function timestamp(signal: Signal) {
  const value = new Date(signal.published_at || signal.created_at).getTime();
  return Number.isNaN(value) ? 0 : value;
}

function unique<T>(items: T[]) {
  return Array.from(new Set(items));
}

function toggleId(ids: number[], id: number) {
  return ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id];
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}
