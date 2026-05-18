export function SectionShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-3xl border border-line bg-panel/80 p-6 shadow-glow backdrop-blur">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-text">{title}</h2>
          {subtitle ? <p className="mt-1 text-sm text-muted">{subtitle}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

