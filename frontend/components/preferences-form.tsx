"use client";

import { useState, useTransition } from "react";

import { savePreferences } from "@/lib/api";

const INTERESTS = [
  "AI",
  "Coding",
  "Startups",
  "Automation",
  "Jobs",
  "Open-source",
  "Funding",
  "Productivity tools",
];

export function PreferencesForm({
  defaultEmail,
  defaultName,
  defaultInterests,
}: {
  defaultEmail: string;
  defaultName?: string | null;
  defaultInterests: string[];
}) {
  const [pending, startTransition] = useTransition();
  const [email, setEmail] = useState(defaultEmail);
  const [name, setName] = useState(defaultName ?? "");
  const [selected, setSelected] = useState<string[]>(defaultInterests);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");

  function toggleInterest(interest: string) {
    setSelected((current) =>
      current.includes(interest)
        ? current.filter((item) => item !== interest)
        : [...current, interest],
    );
    setError("");
  }

  function onSubmit(formData: FormData) {
    setError("");
    setMessage("");
    
    if (!email || !email.trim()) {
      setError("Email is required");
      return;
    }

    if (selected.length === 0) {
      setError("Please select at least one interest");
      return;
    }

    startTransition(async () => {
      try {
        await savePreferences({ email: email.trim(), name: name.trim() || undefined, interests: selected });
        setMessage("Preferences saved! Your radar will adapt on the next refresh.");
        setError("");
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "We could not save preferences right now. Please try again.";
        setError(errorMessage);
        setMessage("");
      }
    });
  }

  return (
    <form action={onSubmit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm text-muted">
          Email
          <input
            value={email}
            onChange={(event) => {
              setEmail(event.target.value);
              setError("");
            }}
            className="w-full rounded-2xl border border-line bg-ink/50 px-4 py-3 text-text outline-none transition focus:border-accent"
            type="email"
            placeholder="your@email.com"
            disabled={pending}
          />
        </label>
        <label className="space-y-2 text-sm text-muted">
          Name
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="w-full rounded-2xl border border-line bg-ink/50 px-4 py-3 text-text outline-none transition focus:border-accent"
            placeholder="Your name (optional)"
            disabled={pending}
          />
        </label>
      </div>
      <div className="flex flex-wrap gap-3">
        {INTERESTS.map((interest) => {
          const active = selected.includes(interest);
          return (
            <button
              key={interest}
              type="button"
              onClick={() => toggleInterest(interest)}
              disabled={pending}
              className={`rounded-full border px-4 py-2 text-sm transition disabled:opacity-50 ${
                active
                  ? "border-accent bg-accent/10 text-accent"
                  : "border-line bg-panelSoft text-muted hover:border-accent/40 hover:text-text"
              }`}
            >
              {interest}
            </button>
          );
        })}
      </div>
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-muted">
          {error ? <span className="text-accentWarm">{error}</span> : message || "Choose the themes you want the system to prioritize."}
        </p>
        <button
          type="submit"
          disabled={pending}
          className="rounded-full bg-accent px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-110 disabled:opacity-60"
        >
          {pending ? "Saving..." : "Save preferences"}
        </button>
      </div>
    </form>
  );
}

