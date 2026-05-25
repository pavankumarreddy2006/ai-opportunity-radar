"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("Application error boundary caught:", error);
  }, [error]);

  return (
    <main className="grid min-h-screen place-items-center bg-ink px-4 text-text">
      <section className="w-full max-w-md rounded-lg border border-line bg-panel p-6 text-center shadow-glow">
        <AlertTriangle className="mx-auto h-9 w-9 text-accentWarm" />
        <h1 className="mt-4 text-2xl font-semibold">Radar hit turbulence</h1>
        <p className="mt-3 text-sm leading-6 text-muted">The app recovered safely. Retry the feed while the API catches up.</p>
        <button
          onClick={reset}
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-110"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      </section>
    </main>
  );
}
