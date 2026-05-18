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

  function toggleInterest(interest: string) {
    setSelected((current) =>
      current.includes(interest)
        ? current.filter((item) => item !== interest)
        : [...current, interest],
    );
  }

  function onSubmit(formData: FormData) {
    formData.get("email");
    startTransition(async () => {
      try {
        await savePreferences({ email, name, interests: selected });
        setMessage("Preferences saved. Your radar will adapt on the next refresh.");
      } catch {
        setMessage("We could not save preferences right now.");
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
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-2xl border border-line bg-ink/50 px-4 py-3 text-text outline-none transition focus:border-accent"
          />
        </label>
        <label className="space-y-2 text-sm text-muted">
          Name
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="w-full rounded-2xl border border-line bg-ink/50 px-4 py-3 text-text outline-none transition focus:border-accent"
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
              className={`rounded-full border px-4 py-2 text-sm transition ${
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
        <p className="text-sm text-muted">{message || "Choose the themes you want the system to prioritize."}</p>
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

