import Link from "next/link";

type Variant = "primary" | "buy" | "secondary" | "ghost" | "tab";
type Size = "sm" | "md";

const base =
  "inline-flex items-center justify-center rounded-full font-bold leading-none whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-60";

const variants: Record<Variant, string> = {
  // button-primary: ink pill with specular shine (marketing CTAs)
  primary: "btn-gloss bg-black text-white active:bg-charcoal disabled:bg-disabled disabled:text-disabled",
  // button-buy-cta: cobalt pill + halo glow — plan-generation flow ONLY
  buy: "btn-gloss btn-cobalt-glow bg-primary text-white active:bg-primary-deep disabled:bg-disabled disabled:text-disabled",
  // button-secondary in aurora world: light glass pill
  secondary: "bg-white/8 text-ink-deep border border-white/25 backdrop-blur-md active:bg-white/15",
  // button-ghost: quieter glass
  ghost: "border border-white/14 bg-white/4 text-ink-deep backdrop-blur-sm active:bg-white/10",
  // button-pill-tab
  tab: "border border-white/16 bg-white/6 text-ink backdrop-blur-md active:bg-white/12",
};

const sizes: Record<Size, string> = {
  // sm ≈ button-pill-tab (8px 16px); md ≈ button-primary (14px 30px, ~44px height)
  sm: "h-9 px-4 text-body-sm",
  md: "h-11 px-8 text-body-sm",
};

type CommonProps = {
  variant?: Variant;
  size?: Size;
  className?: string;
  children: React.ReactNode;
};

const buttonClass = (variant: Variant = "primary", size: Size = "md", className = "") =>
  [base, variants[variant], sizes[size], className].filter(Boolean).join(" ");

export function Button({
  variant,
  size,
  className,
  children,
  type = "button",
  disabled,
  onClick,
}: CommonProps & {
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={buttonClass(variant, size, className)}
    >
      {children}
    </button>
  );
}

export function ButtonLink({
  href,
  variant,
  size,
  className,
  children,
}: CommonProps & { href: string }) {
  return (
    <Link href={href} className={buttonClass(variant, size, className)}>
      {children}
    </Link>
  );
}

export function ButtonExternal({
  href,
  variant,
  size,
  className,
  children,
}: CommonProps & { href: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={buttonClass(variant, size, className)}
    >
      {children}
    </a>
  );
}
