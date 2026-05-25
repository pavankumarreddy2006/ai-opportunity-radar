"use client";

import { useDeferredValue, useEffect, useMemo, useState, useTransition } from "react";
import {
  ArrowUpRight,
  Bookmark,
  Check,
  Clock,
  Flame,
  Heart,
  Moon,
  RefreshCw,
  Search,
  Share2,
  Sparkles,
  Sun,
  UserRound,
  X,
} from "lucide-react";

import { NewsImage } from "@/components/news/NewsImage";
import { getSignals, savePreferences, trackInteraction } from "@/lib/api";
import { PreferenceResponse, Signal, TrendingGroup, WeeklyReport } from "@/lib/types";
import { scoreNews } from "@/services/newsScoring";
import {
  DEFAULT_EMAIL,
  DEFAULT_PROFILE,
  FeedTab,
  RadarProfile,
  addSearch,
  dedupeSignals,
  filterSignals,
  loadProfile,
  rankRecommendations,
  recordBehavior,
  saveProfile,
  savedSignals,
  signalTopics,
  sortLatest,
  sortTrending,
} from "@/services/recommendationEngine";

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

type Toast = { id: number; message: string; tone?: "success" | "error" };

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
  const [visibleCount, setVisibleCount] = useState(10);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
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
      saveProfile(profile);
    }
  }, [profile]);

  useEffect(() => {
    const handle = setTimeout(() => {
      setProfile((current) => addSearch(current, deferredQuery));
      if (deferredQuery.trim().length > 1) {
        void trackInteraction({
          email: profile.email,
          signal_id: 0,
          action: "search",
          query: deferredQuery.trim(),
        });
      }
    }, 600);
    return () => clearTimeout(handle);
  }, [deferredQuery, profile.email]);

  const allSignals = useMemo(() => dedupeSignals([...signals, ...trending.flatMap((group) => group.signals)]), [signals, trending]);
  const tabSignals = useMemo(() => {
    if (activeTab === "trending") {
      return sortTrending(allSignals);
    }
    if (activeTab === "latest") {
      return sortLatest(allSignals);
    }
    if (activeTab === "saved") {
      return savedSignals(allSignals, profile);
    }
    return rankRecommendations(allSignals, profile);
  }, [activeTab, allSignals, profile]);
  const filteredSignals = useMemo(() => filterSignals(tabSignals, deferredQuery), [tabSignals, deferredQuery]);

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

  function record(signal: Signal, action: "like" | "save" | "click" | "share") {
    const readingSeconds = action === "click" ? Math.max(15, Math.round((signal.summary?.what_happened.length ?? 180) / 14)) : 0;
    setProfile((current) => recordBehavior(current, signal, action, readingSeconds));
    void trackInteraction({
      email: profile.email,
      signal_id: signal.id,
      action,
      category: signal.category,
      topics: signalTopics(signal).slice(0, 12),
      reading_seconds: readingSeconds,
    });
  }

  function refreshFeed() {
    startTransition(async () => {
      try {
        const fresh = await getSignals(profile.email);
        setSignals(fresh);
        setVisibleCount(10);
        pushToast("Feed refreshed.");
      } catch {
        pushToast("Could not refresh. Showing cached signals.", "error");
      }
    });
  }

  return (
    <main className={`min-h-screen ${theme === "dark" ? "bg-ink text-text" : "bg-[#F7F8FB] text-[#111827]"}`}>
      <header className={`sticky top-0 z-40 border-b backdrop-blur-xl ${theme === "dark" ? "border-white/10 bg-ink/86" : "border-black/10 bg-white/88"}`}>
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:px-8 lg:flex-row lg:items-center lg:justify-between">
          <BrandHeader />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <label className="relative min-w-0 sm:w-80">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className={`h-11 w-full rounded-lg border pl-10 pr-4 text-sm outline-none transition focus:border-accent ${
                  theme === "dark" ? "border-line bg-panel/80 text-text" : "border-black/10 bg-white text-[#111827]"
                }`}
                placeholder="Search AI agents, SaaS, funding..."
              />
            </label>
            <button
              onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
              className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-line bg-panel/80 text-muted transition hover:border-accent/50 hover:text-text"
              aria-label="Toggle color theme"
              title="Toggle color theme"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button
              onClick={refreshFeed}
              disabled={isPending}
              className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-line bg-panel px-4 text-sm font-semibold text-text transition hover:border-accent/50 disabled:opacity-60"
            >
              <RefreshCw className={`h-4 w-4 ${isPending ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 md:px-8 lg:grid-cols-[17rem_1fr]">
        <RadarSidebar profile={profile} weeklyReport={weeklyReport} onTune={() => setProfile((current) => ({ ...current, onboarded: false }))} />

        <section>
          <FeedTabs activeTab={activeTab} onChange={(tab) => { setActiveTab(tab); setVisibleCount(10); }} />
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
                      record(signal, "share");
                      void shareSignal(signal, pushToast);
                    }}
                  />
                ))}
              </div>
              {visibleCount < filteredSignals.length ? (
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={() => setVisibleCount((count) => count + 8)}
                    className="rounded-lg border border-line bg-panel px-5 py-3 text-sm font-semibold text-text transition hover:border-accent/50"
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
      <ToastStack toasts={toasts} />
    </main>
  );
}

function BrandHeader() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-accent text-ink">
        <Sparkles className="h-5 w-5" />
      </div>
      <div>
        <h1 className="text-lg font-semibold leading-tight md:text-xl">AI Opportunity Radar</h1>
        <p className="text-xs text-muted md:text-sm">Personalized AI news, ranked by opportunity.</p>
      </div>
    </div>
  );
}

function RadarSidebar({ profile, weeklyReport, onTune }: { profile: RadarProfile; weeklyReport: WeeklyReport; onTune: () => void }) {
  return (
    <aside className="lg:sticky lg:top-24 lg:h-[calc(100vh-7rem)]">
      <div className="space-y-4 rounded-lg border border-line bg-panel/80 p-4 shadow-glow">
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
        <button onClick={onTune} className="w-full rounded-lg border border-line px-3 py-2 text-sm text-muted transition hover:border-accent/50 hover:text-text">
          Tune interests
        </button>
      </div>
      <div className="mt-4 rounded-lg border border-line bg-panel/70 p-4">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Weekly brief</p>
        <h2 className="mt-3 text-base font-semibold">{weeklyReport.headline}</h2>
        <p className="mt-2 text-sm leading-6 text-muted">{weeklyReport.executive_summary}</p>
      </div>
    </aside>
  );
}

function FeedTabs({ activeTab, onChange }: { activeTab: FeedTab; onChange: (tab: FeedTab) => void }) {
  const tabs: [FeedTab, string][] = [
    ["for-you", "For You"],
    ["trending", "Trending"],
    ["latest", "Latest"],
    ["saved", "Saved"],
  ];
  return (
    <div className="mb-5 overflow-x-auto">
      <div className="flex min-w-max gap-2">
        {tabs.map(([id, label]) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
              activeTab === id ? "bg-accent text-ink" : "border border-line bg-panel/70 text-muted hover:text-text"
            }`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
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
  const quality = scoreNews(signal);
  const headline = signal.summary?.headline || signal.raw_title;
  return (
    <article className="group overflow-hidden rounded-lg border border-line bg-panelSoft shadow-glow transition duration-200 hover:-translate-y-0.5 hover:border-accent/40">
      <div className="relative">
        <NewsImage src={signal.image_url} category={signal.category} alt={signal.image_alt || headline} priority={priority} />
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
            Trend {quality.trendScore}
          </span>
        </div>
        <h2 className="text-xl font-semibold leading-tight">{headline}</h2>
        <p className="mt-3 text-sm leading-6 text-muted">{quality.aiSummary}</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <InfoBlock label="Why it matters" value={quality.whyItMatters} />
          <InfoBlock label="Opportunity" value={`${quality.opportunityScore}/10 potential`} />
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
    <div className="fixed inset-0 z-50 grid place-items-center bg-ink/82 px-4 backdrop-blur">
      <section className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg border border-line bg-panel p-6 shadow-glow">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold">What topics interest you?</h2>
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

function ToastStack({ toasts }: { toasts: Toast[] }) {
  return (
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
  );
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

function relativeTime(value: string) {
  const hours = Math.max((Date.now() - new Date(value).getTime()) / 36e5, 0);
  if (hours < 1) {
    return "Just now";
  }
  if (hours < 24) {
    return `${Math.round(hours)}h ago`;
  }
  return `${Math.round(hours / 24)}d ago`;
}
