type CardProps = {
  children: React.ReactNode;
  className?: string;
  /** "feature" = card-icon-feature (16px, border, 24px pad); "promo" = dark strip; "soft" = surface-soft 24px tile */
  variant?: "feature" | "promo" | "soft";
};

const styles: Record<string, string> = {
  feature: "rounded-xl border border-hairline-soft bg-canvas p-6",
  promo: "rounded-3xl bg-ink-deep p-8 text-white sm:p-16",
  soft: "rounded-2xl bg-surface-soft p-8",
};

/** Card container per meta/DESIGN.md (flat — no shadow on marketing cards). */
export default function Card({ variant = "feature", className = "", children }: CardProps) {
  return <section className={[styles[variant], className].filter(Boolean).join(" ")}>
    {children}
  </section>;
}
