import { Activity } from "lucide-react";

export default function Loading() {
  return (
    <main className="min-h-screen px-4 py-6 md:px-8 lg:px-12">
      <div className="mx-auto grid min-h-[70vh] max-w-7xl place-items-center">
        <div className="rounded-lg border border-line bg-panel/80 p-8 text-center shadow-glow">
          <Activity className="mx-auto h-8 w-8 animate-pulse text-accent" />
          <p className="mt-4 text-sm font-medium text-text">Loading AI Opportunity Radar</p>
          <p className="mt-2 text-sm text-muted">Preparing the highest-signal updates.</p>
        </div>
      </div>
    </main>
  );
}
