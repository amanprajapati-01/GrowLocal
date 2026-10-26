import Link from "next/link";

type Variant = "primary" | "buy" | "secondary" | "ghost" | "tab";
type Size = "sm" | "md";

const base =
  "inline-flex items-center justify-center rounded-full font-bold leading-none whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-60";

const variants: Record<Variant, string> = {
  // button-primary: black pill (marketing CTAs)
  primary: "bg-black text-white active:bg-charcoal disabled:bg-disabled disabled:text-canvas",
  // button-buy-cta: cobalt pill — plan-generation flow ONLY
  buy: "bg-primary text-white active:bg-primary-deep disabled:bg-disabled disabled:text-canvas",
  // button-secondary: 2px ink outline
  secondary: "border-2 border-ink-deep bg-transparent text-ink-deep active:bg-surface-soft",
  // button-ghost: quieter 2px 12%-alpha outline
  ghost: "border-2 border-ink-deep/12 bg-transparent text-ink-deep active:bg-surface-soft",
  // button-pill-tab
  tab: "border border-hairline bg-canvas text-ink active:bg-surface-soft",
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
