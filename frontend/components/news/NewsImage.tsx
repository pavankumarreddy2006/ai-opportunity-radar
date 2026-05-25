"use client";

import { useMemo, useState } from "react";

const CATEGORY_IMAGES: Record<string, string> = {
  "ai agents": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
  "model releases": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
  "research breakthroughs": "https://images.unsplash.com/photo-1518152006812-edab29b069ac?auto=format&fit=crop&w=1200&q=80",
  "open source ai": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?auto=format&fit=crop&w=1200&q=80",
  "developer tools": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80",
  "ai infrastructure": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
  "startup and funding": "https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=1200&q=80",
  "policy and safety": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1200&q=80",
  finance: "https://images.unsplash.com/photo-1642543348745-03b1219733d9?auto=format&fit=crop&w=1200&q=80",
  crypto: "https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=1200&q=80",
};

const DEFAULT_IMAGE = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80";

type NewsImageProps = {
  src?: string | null;
  category?: string | null;
  alt: string;
  priority?: boolean;
  className?: string;
};

export function NewsImage({ src, category, alt, priority = false, className = "" }: NewsImageProps) {
  const fallbackChain = useMemo(() => buildFallbackChain(src, category), [src, category]);
  const [index, setIndex] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const currentSrc = fallbackChain[index] || DEFAULT_IMAGE;

  return (
    <div className={`relative aspect-[16/9] overflow-hidden bg-panel ${className}`}>
      <div
        className={`absolute inset-0 bg-gradient-to-br from-line via-panelSoft to-ink transition-opacity duration-500 ${
          loaded ? "opacity-0" : "opacity-100 animate-pulse"
        }`}
      />
      <img
        key={currentSrc}
        src={currentSrc}
        alt={alt}
        loading={priority ? "eager" : "lazy"}
        fetchPriority={priority ? "high" : "auto"}
        decoding="async"
        onLoad={() => setLoaded(true)}
        onError={() => {
          setLoaded(false);
          setIndex((current) => (current < fallbackChain.length - 1 ? current + 1 : current));
        }}
        className={`relative h-full w-full object-cover transition duration-700 ${loaded ? "scale-100 opacity-100 blur-0" : "scale-[1.02] opacity-0 blur-sm"}`}
      />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink/50 via-transparent to-transparent" />
    </div>
  );
}

export function categoryFallbackImage(category?: string | null) {
  const key = normalize(category || "");
  return CATEGORY_IMAGES[key] || DEFAULT_IMAGE;
}

function buildFallbackChain(src?: string | null, category?: string | null) {
  const chain = [src, categoryFallbackImage(category), DEFAULT_IMAGE].filter((value): value is string => Boolean(value && value.startsWith("http")));
  return Array.from(new Set(chain));
}

function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}
