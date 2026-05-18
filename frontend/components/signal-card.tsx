import { ArrowUpRight, Sparkles } from "lucide-react";

import { Badge } from "@/components/badge";
import { Signal } from "@/lib/types";

export function SignalCard({ signal, compact = false }: { signal: Signal; compact?: boolean }) {
  return (
    <article className="group rounded-lg border border-line bg-panelSoft p-5 transition hover:border-accent/40 hover:bg-panel">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          <Badge>{signal.source}</Badge>
          <Badge warm>{signal.category}</Badge>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted">
          <Sparkles className="h-4 w-4 text-accent" />
          <span>{signal.importance_score}/100</span>
        </div>
      </div>
      <h3 className="text-lg font-semibold leading-tight text-text">{signal.summary?.headline ?? signal.raw_title}</h3>
      <p className="mt-3 text-sm leading-6 text-muted">{signal.summary?.what_happened ?? "No summary available yet."}</p>
      {!compact ? (
        <>
          <p className="mt-4 text-sm leading-6 text-text/90">{signal.summary?.why_it_matters}</p>
          <div className="mt-4 rounded-lg border border-white/5 bg-ink/30 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-muted">Why you should care</p>
            <p className="mt-2 text-sm leading-6 text-text/95">{signal.summary?.why_you_should_care}</p>
          </div>
          <div className="mt-4 rounded-lg border border-white/5 bg-ink/40 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-muted">Action</p>
            <p className="mt-2 text-sm text-text/95">{signal.summary?.action_recommendation ?? signal.action_recommendation}</p>
          </div>
        </>
      ) : null}
      <div className="mt-5 flex items-center justify-between">
        <span className="text-sm text-muted">Opportunity {signal.opportunity_score}/10</span>
        <a
          href={signal.link}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 text-sm font-medium text-accent transition group-hover:translate-x-0.5"
        >
          Open source
          <ArrowUpRight className="h-4 w-4" />
        </a>
      </div>
    </article>
  );
}
