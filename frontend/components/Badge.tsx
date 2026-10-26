type BadgeVariant = "free" | "warning" | "attention" | "critical" | "neutral";

const styles: Record<BadgeVariant, string> = {
  // badge-success (green) for a FREE channel tag
  free: "bg-success text-white",
  // badge-promo-yellow: warning bg + ink text (alert copy stays dark for contrast)
  warning: "bg-warning text-black",
  attention: "bg-attention text-black",
  critical: "bg-critical text-white",
  neutral: "bg-white/10 text-steel",
};

/** caption-bold pill badges (badge-success / promo-yellow / attention / critical). */
export default function Badge({
  variant = "neutral",
  className = "",
  children,
}: {
  variant?: BadgeVariant;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={[
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 ds-caption-bold",
        styles[variant],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </span>
  );
}
