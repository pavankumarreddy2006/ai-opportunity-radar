export type SummaryPayload = {
  headline: string;
  what_happened: string;
  why_it_matters: string;
  why_you_should_care: string;
  action_recommendation: string;
  opportunity_score: number;
};

export type Signal = {
  id: number;
  category: string;
  importance_score: number;
  opportunity_score: number;
  action_recommendation: string | null;
  created_at: string;
  raw_title: string;
  source: string;
  link: string;
  tags: string[];
  published_at: string | null;
  summary: SummaryPayload | null;
};

export type TrendingGroup = {
  section: string;
  signals: Signal[];
};

export type PreferenceResponse = {
  id: number;
  email: string;
  name: string | null;
  interests: { name: string }[];
};

export type DashboardResponse = {
  top_signals: Signal[];
  trending: TrendingGroup[];
  interests: string[];
};

export type WeeklyReport = {
  headline: string;
  executive_summary: string;
  top_categories: string[];
  signals: Signal[];
};
