"use client";

import { useTranslations } from "next-intl";
import { Button } from "@/components/Button";

/** Screen-level error (errorTitle + message + retry). code-aware copy. */
export default function ErrorState({
  code,
  onRetry,
}: {
  code?: string | null;
  onRetry?: () => void;
}) {
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const known = ["network", "rateLimited", "planNotFound", "budgetAboveTotal", "generic"];
  const key = code && code !== "unknown" && known.includes(code) ? code : "generic";

  return (
    <div
      role="alert"
      className="mx-auto flex max-w-md flex-col items-center gap-3 rounded-xl border border-hairline-soft bg-canvas p-8 text-center"
    >
      <span aria-hidden className="text-3xl">:(</span>
      <h2 className="ds-subtitle-lg text-ink-deep">{tCommon("errorTitle")}</h2>
      <p className="text-charcoal ds-body-sm">{tErrors(key)}</p>
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          {tCommon("tryAgain")}
        </Button>
      ) : null}
    </div>
  );
}

export function EmptyState({
  title,
  sub,
  action,
}: {
  title: string;
  sub?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-3 rounded-xl border border-hairline-soft bg-surface-soft p-8 text-center">
      <span aria-hidden className="text-3xl">☰</span>
      <h2 className="ds-subtitle-lg text-ink-deep">{title}</h2>
      {sub ? <p className="text-charcoal ds-body-sm">{sub}</p> : null}
      {action}
    </div>
  );
}
