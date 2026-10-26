/**
 * Shared formatting helpers — Indian-locale money and dates.
 */

/**
 * Format a number with Indian digit grouping (1,00,000) as ₹.
 * Example: formatInr(2700) === "₹2,700"
 */
export function formatInr(amount: number): string {
  const rounded = Math.round(amount);
  return `₹${rounded.toLocaleString("en-IN")}`;
}

/** "₹2,700" without the symbol, for chart axes. */
export function formatInrBare(amount: number): string {
  return Math.round(amount).toLocaleString("en-IN");
}

/** "₹0–₹500" style range for estimate labels. */
export function formatInrRange(lo: number, hi: number): string {
  if (lo === hi) return formatInr(lo);
  return `${formatInr(lo)}–${formatInr(hi)}`;
}

/** Monotonic short date: 12 Jan 2026 (locale-dependent month names come from ICU). */
export function formatDateShort(iso: string, locale: string = "en"): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(locale === "hi" ? "hi-IN" : "en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
