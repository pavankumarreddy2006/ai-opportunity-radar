import clsx from "clsx";

export function Badge({ children, warm = false }: { children: React.ReactNode; warm?: boolean }) {
  return (
    <span
      className={clsx(
        "inline-flex rounded-full border px-3 py-1 text-xs font-medium tracking-wide",
        warm ? "border-accentWarm/30 bg-accentWarm/10 text-accentWarm" : "border-accent/30 bg-accent/10 text-accent",
      )}
    >
      {children}
    </span>
  );
}

