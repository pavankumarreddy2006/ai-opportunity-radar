import type { ReactNode } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Bolt,
  BookOpen,
  BrainCircuit,
  BriefcaseBusiness,
  CalendarDays,
  Compass,
  Github,
  HeartPulse,
  Wrench,
} from "lucide-react";

import { PreferencesForm } from "@/components/preferences-form";
import { SectionShell } from "@/components/section-shell";
import { SignalCard } from "@/components/signal-card";
import { getPreferences, getSignals, getTrending, getWeeklyReport } from "@/lib/api";

const DEFAULT_EMAIL = "demo@ainewscollector.ai";

export default async function HomePage() {
  const [signals, trending, preferences, weeklyReport] = await Promise.all([
    getSignals(DEFAULT_EMAIL),
    getTrending(),
    getPreferences(DEFAULT_EMAIL),
    getWeeklyReport(DEFAULT_EMAIL),
  ]);

  const preferenceNames = preferences?.interests.map((item) => item.name) ?? ["AI", "Coding", "Startups"];

  return (
    <main className="min-h-screen px-4 py-6 md:px-8 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <section className="relative overflow-hidden rounded-lg border border-white/10 bg-panel px-6 py-8 md:px-10 md:py-12">
          <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(121,226,160,0.16),transparent_34%),linear-gradient(315deg,rgba(244,201,109,0.12),transparent_28%)]" />
          <div className="relative grid gap-8 lg:grid-cols-[1.4fr_0.8fr]">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-2 text-sm text-accent">
                <Compass className="h-4 w-4" />
                AI opportunity intelligence
              </div>
              <h1 className="mt-6 max-w-3xl text-4xl font-semibold leading-tight text-text md:text-6xl">
                AI Opportunity Radar
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-7 text-muted md:text-lg">
                Get only the most important AI updates worth your attention.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href="/dashboard"
                  className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-accent px-5 text-sm font-semibold text-ink transition hover:bg-accent/90"
                >
                  Open Dashboard
                  <ArrowRight className="h-4 w-4" />
                </a>
                <a
                  href="/docs"
                  className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-5 text-sm font-semibold text-text transition hover:border-accent/40"
                >
                  <BookOpen className="h-4 w-4" />
                  API Docs
                </a>
                <a
                  href="/health"
                  className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-5 text-sm font-semibold text-text transition hover:border-accent/40"
                >
                  <HeartPulse className="h-4 w-4" />
                  Health Check
                </a>
              </div>
              <div className="mt-8 grid gap-4 sm:grid-cols-3">
                <MetricCard icon={<BrainCircuit className="h-5 w-5" />} label="AI-ranked" value="1-hour refresh" />
                <MetricCard icon={<Bolt className="h-5 w-5" />} label="Signal-first" value="Top 5 daily" />
                <MetricCard icon={<BarChart3 className="h-5 w-5" />} label="Opportunity" value="Actionable scores" />
              </div>
            </div>
            <div className="rounded-lg border border-white/10 bg-ink/50 p-5 backdrop-blur">
              <p className="text-sm uppercase tracking-[0.25em] text-muted">Current Focus</p>
              <div className="mt-4 flex flex-wrap gap-3">
                {preferenceNames.map((interest) => (
                  <span key={interest} className="rounded-full bg-white/5 px-4 py-2 text-sm text-text">
                    {interest}
                  </span>
                ))}
              </div>
              <div className="mt-6 space-y-3">
                {signals.slice(0, 3).map((signal, index) => (
                  <div key={signal.id} className="rounded-lg border border-white/5 bg-panelSoft px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted">Priority {index + 1}</p>
                    <p className="mt-2 text-sm font-medium text-text">{signal.summary?.headline ?? signal.raw_title}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5" aria-label="Radar sections">
          <FeatureCard title="Top 5 AI Updates" detail="The shortlist worth acting on today." icon={<Bolt className="h-5 w-5" />} />
          <FeatureCard title="Trending Topics" detail="Themes with cross-source momentum." icon={<Activity className="h-5 w-5" />} />
          <FeatureCard title="AI Tool Trends" detail="Developer tools, agents, and infrastructure." icon={<Wrench className="h-5 w-5" />} />
          <FeatureCard title="Open Source AI" detail="Repos and infrastructure shifts gaining traction." icon={<Github className="h-5 w-5" />} />
          <FeatureCard title="Latest Important Updates" detail="Fresh signals with fallback data when sources wake." icon={<CalendarDays className="h-5 w-5" />} />
        </section>

        <div className="mt-8 grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <SectionShell title="Top 5 AI Updates Today" subtitle="A ranked shortlist built for immediate attention.">
            <div className="grid gap-4">
              {signals.map((signal) => (
                <SignalCard key={signal.id} signal={signal} />
              ))}
            </div>
          </SectionShell>

          <SectionShell title="Weekly Digest" subtitle={weeklyReport.executive_summary}>
              <div className="rounded-lg border border-line bg-panelSoft p-5">
              <div className="flex items-start gap-3">
                <CalendarDays className="mt-1 h-5 w-5 text-accentWarm" />
                <div>
                  <h2 className="text-lg font-semibold text-text">{weeklyReport.headline}</h2>
                  <p className="mt-3 text-sm leading-6 text-muted">
                    Top themes: {weeklyReport.top_categories.join(", ") || "AI, coding, startups"}.
                  </p>
                </div>
              </div>
            </div>
          </SectionShell>

          <SectionShell title="User Preferences" subtitle="Shape what the radar prioritizes on every refresh.">
            <PreferencesForm
              defaultEmail={preferences?.email ?? DEFAULT_EMAIL}
              defaultName={preferences?.name}
              defaultInterests={preferences?.interests.map((item) => item.name) ?? ["AI", "Coding", "Startups"]}
            />
          </SectionShell>
        </div>

        <div className="mt-8 grid gap-8 xl:grid-cols-2">
          {trending.map((group) => (
            <SectionShell key={group.section} title={group.section}>
              <div className="grid gap-4">
                {group.signals.length > 0 ? (
                  group.signals.map((signal) => <SignalCard key={signal.id} signal={signal} compact />)
                ) : (
                  <EmptyState section={group.section} />
                )}
              </div>
            </SectionShell>
          ))}
        </div>
      </div>
    </main>
  );
}

function MetricCard({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-3 text-accent">
        {icon}
        <span className="text-sm text-muted">{label}</span>
      </div>
      <p className="mt-3 text-lg font-semibold text-text">{value}</p>
    </div>
  );
}

function FeatureCard({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <article className="rounded-lg border border-line bg-panel/75 p-5 shadow-glow">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">{icon}</div>
      <h2 className="text-base font-semibold leading-snug text-text">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-muted">{detail}</p>
    </article>
  );
}

function EmptyState({ section }: { section: string }) {
  const icon =
    section === "Latest Open Source AI" ? (
      <Github className="h-6 w-6" />
    ) : section === "Startup and Funding" ? (
      <BriefcaseBusiness className="h-6 w-6" />
    ) : (
      <Compass className="h-6 w-6" />
    );

  return (
    <div className="rounded-lg border border-dashed border-line bg-panelSoft/70 p-8 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-white/5 text-accent">{icon}</div>
      <p className="mt-4 text-base font-medium text-text">No fresh signals here yet.</p>
      <p className="mt-2 text-sm text-muted">Run the hourly refresh or broaden your sources to populate {section.toLowerCase()}.</p>
    </div>
  );
}
