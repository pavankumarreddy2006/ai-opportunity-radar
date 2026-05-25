import { Signal } from "@/lib/types";

export type QualityScore = {
  aiSummary: string;
  whyItMatters: string;
  opportunityScore: number;
  trendScore: number;
  qualityScore: number;
  clickbaitRisk: number;
  spamRisk: number;
};

const CLICKBAIT_PATTERNS = [
  /\b(shocking|insane|secret|you won't believe|game[- ]?changer|mind[- ]?blowing)\b/i,
  /!{2,}/,
  /\?{2,}/,
];

const SPAM_PATTERNS = [
  /\b(buy now|limited time|guaranteed|100% free|make money fast)\b/i,
  /\b(casino|loan|viagra)\b/i,
];

export function scoreNews(signal: Signal): QualityScore {
  const text = `${signal.raw_title} ${signal.summary?.headline ?? ""} ${signal.summary?.what_happened ?? ""}`;
  const titleLengthPenalty = signal.raw_title.length > 180 ? 12 : 0;
  const missingSummaryPenalty = signal.summary ? 0 : 10;
  const clickbaitRisk = clamp(
    CLICKBAIT_PATTERNS.reduce((score, pattern) => score + (pattern.test(text) ? 22 : 0), 0) + titleLengthPenalty,
    0,
    100,
  );
  const spamRisk = clamp(SPAM_PATTERNS.reduce((score, pattern) => score + (pattern.test(text) ? 35 : 0), 0), 0, 100);
  const qualityScore = clamp(
    signal.importance_score * 0.42 +
      signal.opportunity_score * 4 +
      signal.trend_score * 0.18 +
      freshnessScore(signal) * 0.16 -
      clickbaitRisk * 0.22 -
      spamRisk * 0.32 -
      missingSummaryPenalty,
    0,
    100,
  );

  return {
    aiSummary: buildSummary(signal),
    whyItMatters: signal.summary?.why_it_matters || "This update may change what builders should learn, monitor, or ship next.",
    opportunityScore: clamp(Math.round(signal.opportunity_score || signal.summary?.opportunity_score || qualityScore / 10), 1, 10),
    trendScore: clamp(Math.round(signal.trend_score || signal.importance_score * 0.7), 0, 100),
    qualityScore: Math.round(qualityScore),
    clickbaitRisk,
    spamRisk,
  };
}

export function isLowQuality(signal: Signal) {
  const score = scoreNews(signal);
  return score.spamRisk >= 70 || score.clickbaitRisk >= 75 || score.qualityScore < 18;
}

function buildSummary(signal: Signal) {
  const primary = signal.summary?.what_happened || signal.summary?.headline || signal.raw_title;
  const secondary = signal.summary?.why_you_should_care || signal.action_recommendation;
  return [primary, secondary].filter(Boolean).join(" ");
}

function freshnessScore(signal: Signal) {
  const date = new Date(signal.published_at || signal.created_at).getTime();
  if (Number.isNaN(date)) {
    return 30;
  }
  const hours = Math.max((Date.now() - date) / 36e5, 0);
  return clamp(100 - hours * 2.4, 0, 100);
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}
