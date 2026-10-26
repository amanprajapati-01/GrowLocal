type CardProps = {
  children: React.ReactNode;
  className?: string;
  /** "feature" = frosted glass tile; "solid" = nested dense panel (no double blur); "hero" = dark aurora hero */
  variant?: "feature" | "solid" | "hero";
};

const styles: Record<string, string> = {
  feature: "glass rounded-xl p-6",
  solid: "glass-solid rounded-xl p-6",
  hero: "glass-hero rounded-3xl p-8 sm:p-16 text-white",
};

/** Card container — flat glass per the Aurora Glass variant layer (no marketing shadows). */
export default function Card({ variant = "feature", className = "", children }: CardProps) {
  return <section className={[styles[variant], className].filter(Boolean).join(" ")}>
    {children}
  </section>;
}
