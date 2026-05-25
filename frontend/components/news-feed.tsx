"use client";

import { useDeferredValue, useEffect, useMemo, useState, useTransition } from "react";
import {
  ArrowUpRight,
  Bookmark,
  Check,
  Clock,
  Flame,
  Heart,
  RefreshCw,
  Search,
  Share2,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";

import { getSignals, savePreferences } from "@/lib/api";
import { PreferenceResponse, Signal, TrendingGroup, WeeklyReport } from "@/lib/types";

const DEFAULT_EMAIL = "demo@ainewscollector.ai";
const STORAGE_KEY = "ai-radar-profile-v2";

const INTERESTS = [
  "AI Tools",
  "Startups",
  "Automation",
  "Coding",
  "SaaS",
  "Business Ideas",
  "Side Hustles",
  "Machine Learning",
  "Prompt Engineering",
  "Finance",
  "Crypto",
  "Tech News",
  "Productivity",
  "YouTube Automation",
  "Content Creation",
];

type FeedTab = "for-you" | "trending" | "latest" | "saved";

type RadarProfile = {
  email: string;
  interests: string[];
  likedIds: number[];
  savedIds: number[];
  clickedIds: number[];
  topicWeights: Record<string, number>;
  onboarded: boolean;
};

type Toast = { id: number; message: string; tone?: "success" | "error" };

const DEFAULT_PROFILE: RadarProfile = {
  email: DEFAULT_EMAIL,
  interests: [],
  likedIds: [],
  savedIds: [],
  clickedIds: [],
  topicWeights: {},
  onboarded: false,
};

const CATEGORY_IMAGES: Record<string, string> = {
  "ai agents": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
  "model releases": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
  "research breakthroughs": "https://images.unsplash.com/photo-1518152006812-edab29b069ac?auto=format&fit=crop&w=1200&q=80",
  "open source ai": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?auto=format&fit=crop&w=1200&q=80",
  "developer tools": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80",
  "startup and funding": "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=80",
};

export function NewsFeed({
  initialSignals,
  trending,
  preferences,
  weeklyReport,
}: {
  initialSignals: Signal[];
  trending: TrendingGroup[];
  preferences: PreferenceResponse | null;
  weeklyReport: WeeklyReport;
}) {
  const [signals, setSignals] = useState(initialSignals);
  const [profile, setProfile] = useState<RadarProfile>(DEFAULT_PROFILE);
  const [activeTab, setActiveTab] = useState<FeedTab>("for-you");
  const [query, setQuery] = useState("");
  const [visibleCount, setVisibleCount] = useState(9);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [isPending, startTransition] = useTransition();
  const deferredQuery = useDeferredValue(query);

  useEffect(() => {
    const stored = loadProfile();
    const backendInterests = preferences?.interests.map((interest) => interest.name) ?? [];
    const merged = {
      ...DEFAULT_PROFILE,
      ...stored,
      email: stored.email || preferences?.email || DEFAULT_EMAIL,
      interests: stored.interests.length ? stored.interests : backendInterests,
      onboarded: stored.onboarded || backendInterests.length > 0,
    };
    setProfile(merged);
  }, [preferences]);

  useEffect(() => {
    if (profile.email) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    }
  }, [profile]);

  const allSignals = useMemo(() => dedupeSignals(signals, trending.flatMap((group) => group.signals)), [signals, trending]);
  const rankedSignals = useMemo(() => rankSignals(allSignals, profile), [allSignals, profile]);
  const latestSignals = useMemo(
    () => [...allSignals].sort((a, b) => new Date(b.published_at ?? b.created_at).getTime() - new Date(a.published_at ?? a.created_at).getTime()),
    [allSignals],
  );
  const trendingSignals = useMemo(
    () => [...allSignals].sort((a, b) => b.trend_score + b.importance_score - (a.trend_score + a.importance_score)),
    [allSignals],
  );

  const tabSignals =
    activeTab === "for-you"
      ? rankedSignals
      : activeTab === "trending"
        ? trendingSignals
        : activeTab === "latest"
          ? latestSignals
          : allSignals.filter((signal) => profile.savedIds.includes(signal.id));

  const filteredSignals = useMemo(() => {
    const search = deferredQuery.trim().toLowerCase();
    if (!search) {
      return tabSignals;
    }
    return tabSignals.filter((signal) =>
      [signal.raw_title, signal.summary?.headline, signal.summary?.what_happened, signal.category, signal.source, ...signal.tags]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(search),
    );
  }, [deferredQuery, tabSignals]);

  function pushToast(message: string, tone: Toast["tone"] = "success") {
    const id = Date.now();
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), 3200);
  }

  function saveOnboarding(interests: string[]) {
    const nextProfile = { ...profile, interests, onboarded: true };
    setProfile(nextProfile);
    startTransition(async () => {
      try {
        await savePreferences({ email: nextProfile.email, interests });
        pushToast("Your feed is personalized.");
      } catch {
        pushToast("Saved locally. Backend sync will retry when the API is awake.", "error");
      }
    });
  }

  function record(signal: Signal, action: "like" | "save" | "click") {
    setProfile((current) => {
      const topicWeights = { ...current.topicWeights };
      for (const topic of signalTopics(signal)) {
        topicWeights[topic] = (topicWeights[topic] ?? 0) + (action === "click" ? 1 : 2);
      }
      return {
        ...current,
        likedIds: action === "like" ? toggleId(current.likedIds, signal.id) : current.likedIds,
        savedIds: action === "save" ? toggleId(current.savedIds, signal.id) : current.savedIds,
        clickedIds: action === "click" ? unique([...current.clickedIds, signal.id]).slice(-80) : current.clickedIds,
        topicWeights,
      };
    });
  }

  function refreshFeed() {
    startTransition(async () => {
      try {
        const fresh = await getSignals(profile.email);
        setSignals(fresh);
        setVisibleCount(9);
        pushToast("Feed refreshed.");
      } catch {
        pushToast("Could not refresh. Showing cached signals.", "error");
      }
    });
  }

  return (
    <main className="min-h-screen bg-ink text-text">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-ink/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:px-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-accent text-ink">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold leading-tight md:text-xl">AI Opportunity Radar</h1>
              <p className="text-xs text-muted md:text-sm">Personalized AI news, ranked by opportunity.</p>
            </div>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <label className="relative min-w-0 sm:w-72">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="h-11 w-full rounded-lg border border-line bg-panel/80 pl-10 pr-4 text-sm text-text outline-none transition focus:border-accent"
                placeholder="Search AI agents, SaaS, funding..."
              />
            </label>
            <button
              onClick={refreshFeed}
              disabled={isPending}
              className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-line bg-panel px-4 text-sm font-semibold transition hover:border-accent/50 disabled:opacity-60"
            >
              <RefreshCw className={`h-4 w-4 ${isPending ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 md:px-8 lg:grid-cols-[17rem_1fr]">
        <aside className="lg:sticky lg:top-24 lg:h-[calc(100vh-7rem)]">
          <div className="space-y-4 rounded-lg border border-line bg-panel/80 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <UserRound className="h-4 w-4 text-accent" />
              Your Signals
            </div>
            <div className="flex flex-wrap gap-2">
              {(profile.interests.length ? profile.interests : ["AI Tools", "Startups", "Automation"]).map((interest) => (
                <span key={interest} className="rounded-full border border-accent/20 bg-accent/10 px-3 py-1 text-xs text-accent">
                  {interest}
                </span>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <Stat label="Saved" value={profile.savedIds.length} />
              <Stat label="Liked" value={profile.likedIds.length} />
              <Stat label="Read" value={profile.clickedIds.length} />
            </div>
            <button
              onClick={() => setProfile((current) => ({ ...current, onboarded: false }))}
              className="w-full rounded-lg border border-line px-3 py-2 text-sm text-muted transition hover:border-accent/50 hover:text-text"
            >
              Tune interests
            </button>
          </div>
          <div className="mt-4 rounded-lg border border-line bg-panel/70 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-muted">Weekly brief</p>
            <h2 className="mt-3 text-base font-semibold">{weeklyReport.headline}</h2>
            <p className="mt-2 text-sm leading-6 text-muted">{weeklyReport.executive_summary}</p>
          </div>
        </aside>

        <section>
          <div className="mb-5 overflow-x-auto">
            <div className="flex min-w-max gap-2">
              {[
                ["for-you", "For You"],
                ["trending", "Trending"],
                ["latest", "Latest"],
                ["saved", "Saved"],
              ].map(([id, label]) => (
                <button
                  key={id}
                  onClick={() => {
                    setActiveTab(id as FeedTab);
                    setVisibleCount(9);
                  }}
                  className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
                    activeTab === id ? "bg-accent text-ink" : "border border-line bg-panel/70 text-muted hover:text-text"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {isPending && signals.length === 0 ? <SkeletonGrid /> : null}
          {filteredSignals.length > 0 ? (
            <>
              <div className="grid gap-5 xl:grid-cols-2">
                {filteredSignals.slice(0, visibleCount).map((signal, index) => (
                  <NewsCard
                    key={`${signal.id}-${activeTab}`}
                    signal={signal}
                    priority={index < 2}
                    liked={profile.likedIds.includes(signal.id)}
                    saved={profile.savedIds.includes(signal.id)}
                    onLike={() => record(signal, "like")}
                    onSave={() => record(signal, "save")}
                    onOpen={() => record(signal, "click")}
                    onShare={() => {
                      void shareSignal(signal, pushToast);
                    }}
                  />
                ))}
              </div>
              {visibleCount < filteredSignals.length ? (
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={() => setVisibleCount((count) => count + 6)}
                    className="rounded-lg border border-line bg-panel px-5 py-3 text-sm font-semibold transition hover:border-accent/50"
                  >
                    Load more signals
                  </button>
                </div>
              ) : null}
            </>
          ) : (
            <EmptyState tab={activeTab} query={deferredQuery} />
          )}
        </section>
      </div>

      {!profile.onboarded ? <Onboarding initial={profile.interests} pending={isPending} onSave={saveOnboarding} /> : null}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`rounded-lg border px-4 py-3 text-sm shadow-glow ${
              toast.tone === "error" ? "border-accentWarm/40 bg-[#2A2114] text-accentWarm" : "border-accent/30 bg-[#10261E] text-accent"
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </main>
  );
}

function NewsCard({
  signal,
  priority,
  liked,
  saved,
  onLike,
  onSave,
  onShare,
  onOpen,
}: {
  signal: Signal;
  priority: boolean;
  liked: boolean;
  saved: boolean;
  onLike: () => void;
  onSave: () => void;
  onShare: () => void;
  onOpen: () => void;
}) {
  const [imageSrc, setImageSrc] = useState(signal.image_url || fallbackImage(signal.category));
  const headline = signal.summary?.headline || signal.raw_title;
  return (
    <article className="group overflow-hidden rounded-lg border border-line bg-panelSoft shadow-glow transition duration-200 hover:-translate-y-0.5 hover:border-accent/40">
      <div className="relative aspect-[16/9] overflow-hidden bg-panel">
        <div className="absolute inset-0 animate-pulse bg-gradient-to-br from-line via-panelSoft to-ink" />
        <img
          src={imageSrc}
          alt={signal.image_alt || headline}
          loading={priority ? "eager" : "lazy"}
          decoding="async"
          onError={() => setImageSrc(fallbackImage(signal.category))}
          className="relative h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]"
        />
        <div className="absolute left-3 top-3 rounded-full bg-ink/80 px-3 py-1 text-xs font-semibold text-accent backdrop-blur">
          {signal.category}
        </div>
      </div>
      <div className="p-5">
        <div className="mb-3 flex flex-wrap items-center gap-3 text-xs text-muted">
          <span className="font-semibold text-text">{signal.source}</span>
          <span className="inline-flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {relativeTime(signal.published_at || signal.created_at)}
          </span>
          <span className="inline-flex items-center gap-1">
            <Flame className="h-3.5 w-3.5 text-accentWarm" />
            Trend {signal.trend_score}
          </span>
        </div>
        <h2 className="text-xl font-semibold leading-tight">{headline}</h2>
        <p className="mt-3 text-sm leading-6 text-muted">{signal.summary?.what_happened || "Summary is being prepared for this signal."}</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <InfoBlock label="Why it matters" value={signal.summary?.why_it_matters || "This signal is fresh, relevant, and worth tracking."} />
          <InfoBlock label="Opportunity" value={`${signal.opportunity_score}/10 potential`} />
        </div>
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex gap-2">
            <IconButton active={liked} label="Like" onClick={onLike}>
              <Heart className="h-4 w-4" />
            </IconButton>
            <IconButton active={saved} label="Save" onClick={onSave}>
              <Bookmark className="h-4 w-4" />
            </IconButton>
            <IconButton label="Share" onClick={onShare}>
              <Share2 className="h-4 w-4" />
            </IconButton>
          </div>
          <a
            href={signal.link}
            target="_blank"
            rel="noreferrer"
            onClick={onOpen}
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-ink transition hover:brightness-110"
          >
            Read
            <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>
      </div>
    </article>
  );
}

function Onboarding({ initial, pending, onSave }: { initial: string[]; pending: boolean; onSave: (interests: string[]) => void }) {
  const [selected, setSelected] = useState(initial.length ? initial : ["AI Tools", "Startups", "Automation"]);
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ink/80 px-4 backdrop-blur">
      <section className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg border border-line bg-panel p-6 shadow-glow">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold">What are you interested in?</h2>
            <p className="mt-2 text-sm leading-6 text-muted">Pick a few themes and the feed will adapt as you read, like, and save.</p>
          </div>
          <button onClick={() => onSave(selected)} className="rounded-lg border border-line p-2 text-muted hover:text-text" aria-label="Close onboarding">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {INTERESTS.map((interest) => {
            const active = selected.includes(interest);
            return (
              <button
                key={interest}
                onClick={() => setSelected((current) => (current.includes(interest) ? current.filter((item) => item !== interest) : [...current, interest]))}
                className={`flex min-h-12 items-center justify-between rounded-lg border px-4 text-left text-sm font-semibold transition ${
                  active ? "border-accent bg-accent/10 text-accent" : "border-line bg-ink/40 text-muted hover:text-text"
                }`}
              >
                {interest}
                {active ? <Check className="h-4 w-4" /> : null}
              </button>
            );
          })}
        </div>
        <button
          disabled={pending || selected.length === 0}
          onClick={() => onSave(selected)}
          className="mt-6 w-full rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-110 disabled:opacity-60"
        >
          {pending ? "Saving..." : "Personalize my feed"}
        </button>
      </section>
    </div>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/5 bg-ink/35 p-3">
      <p className="text-xs uppercase tracking-[0.16em] text-muted">{label}</p>
      <p className="mt-2 text-sm leading-5 text-text/90">{value}</p>
    </div>
  );
}

function IconButton({ active, label, onClick, children }: { active?: boolean; label: string; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className={`flex h-10 w-10 items-center justify-center rounded-lg border transition ${
        active ? "border-accent bg-accent/10 text-accent" : "border-line bg-ink/40 text-muted hover:border-accent/40 hover:text-text"
      }`}
    >
      {children}
    </button>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-line bg-ink/40 p-3">
      <p className="text-lg font-semibold">{value}</p>
      <p className="text-xs text-muted">{label}</p>
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid gap-5 xl:grid-cols-2">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="overflow-hidden rounded-lg border border-line bg-panelSoft">
          <div className="aspect-[16/9] animate-pulse bg-line" />
          <div className="space-y-3 p-5">
            <div className="h-4 w-32 animate-pulse rounded bg-line" />
            <div className="h-7 w-4/5 animate-pulse rounded bg-line" />
            <div className="h-4 w-full animate-pulse rounded bg-line" />
            <div className="h-4 w-2/3 animate-pulse rounded bg-line" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ tab, query }: { tab: FeedTab; query: string }) {
  return (
    <div className="rounded-lg border border-dashed border-line bg-panel/70 p-10 text-center">
      <Sparkles className="mx-auto h-8 w-8 text-accent" />
      <h2 className="mt-4 text-xl font-semibold">No signals found</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted">
        {query ? `No articles match "${query}".` : tab === "saved" ? "Save articles to build your reading queue." : "The API may be waking up; fallback data will appear on refresh."}
      </p>
    </div>
  );
}

function rankSignals(signals: Signal[], profile: RadarProfile) {
  const interests = profile.interests.map(normalize);
  return [...signals].sort((a, b) => scoreSignal(b, interests, profile) - scoreSignal(a, interests, profile));
}

function scoreSignal(signal: Signal, interests: string[], profile: RadarProfile) {
  const topics = signalTopics(signal);
  const interestMatch = topics.some((topic) => interests.some((interest) => topic.includes(interest) || interest.includes(topic))) ? 30 : 0;
  const clicked = profile.clickedIds.includes(signal.id) ? 12 : 0;
  const likedTopics = topics.reduce((sum, topic) => sum + (profile.topicWeights[topic] ?? 0), 0);
  const freshness = Math.max(0, 20 - ageHours(signal.published_at || signal.created_at) / 3);
  const engagement = signal.importance_score * 0.2 + signal.opportunity_score * 2 + signal.trend_score * 0.15;
  return interestMatch + clicked + likedTopics + freshness + engagement;
}

function signalTopics(signal: Signal) {
  return unique([signal.category, ...signal.tags, ...(signal.summary?.headline ?? "").split(" ")]
    .map(normalize)
    .filter((topic) => topic.length > 2));
}

function dedupeSignals(...groups: Signal[][]) {
  const seen = new Set<string>();
  const output: Signal[] = [];
  for (const signal of groups.flat()) {
    const key = `${normalize(signal.raw_title)}-${signal.link}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    output.push(signal);
  }
  return output;
}

function loadProfile(): RadarProfile {
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

function fallbackImage(category: string) {
  return CATEGORY_IMAGES[normalize(category)] || "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80";
}

function relativeTime(value: string) {
  const hours = ageHours(value);
  if (hours < 1) {
    return "Just now";
  }
  if (hours < 24) {
    return `${Math.round(hours)}h ago`;
  }
  return `${Math.round(hours / 24)}d ago`;
}

function ageHours(value: string) {
  return Math.max((Date.now() - new Date(value).getTime()) / 36e5, 0);
}

function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function unique<T>(items: T[]) {
  return Array.from(new Set(items));
}

function toggleId(ids: number[], id: number) {
  return ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id];
}

async function shareSignal(signal: Signal, pushToast: (message: string, tone?: Toast["tone"]) => void) {
  const title = signal.summary?.headline || signal.raw_title;
  try {
    if (navigator.share) {
      await navigator.share({ title, url: signal.link });
    } else {
      await navigator.clipboard.writeText(signal.link);
      pushToast("Link copied.");
    }
  } catch {
    pushToast("Share cancelled.", "error");
  }
}
