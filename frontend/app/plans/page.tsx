"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useEffect, useState } from "react";
import TopBar from "@/components/TopBar";
import Card from "@/components/Card";
import ErrorState, { EmptyState } from "@/components/ErrorState";
import { SkeletonCard } from "@/components/Skeleton";
import { ButtonLink } from "@/components/Button";
import { listPlans, ApiError, type PlanSummary } from "@/lib/api";
import { formatDateShort, formatInr } from "@/lib/format";

const GOAL_LABEL: Record<string, string> = {
  more_walk_ins: "goal_more_walk_ins",
  online_orders: "goal_online_orders",
  repeat_customers: "goal_repeat_customers",
  brand_awareness: "goal_brand_awareness",
};

/** S7 — saved plans list (belongs to the current backend user). */
export default function PlansPage() {
  const t = useTranslations("plans");
  const tW = useTranslations("wizard");
  const [plans, setPlans] = useState<PlanSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    listPlans()
      .then((res) => {
        if (alive) setPlans(res.plans ?? []);
      })
      .catch((e) => {
        if (alive)
          setError(e instanceof ApiError ? (e.code === "network" ? "network" : "generic") : "generic");
      });
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />
      <main className="mx-auto w-full max-w-2xl flex-1 px-5 pb-24">
        <h1 className="mt-6 ds-heading text-ink-deep">{t("title")}</h1>

        <div className="mt-6 flex flex-col gap-3">
          {plans === null && !error
            ? [0, 1, 2].map((i) => <SkeletonCard key={i} />)
            : null}

          {error ? <ErrorState code={error} onRetry={() => window.location.reload()} /> : null}

          {plans?.length === 0 ? (
            <EmptyState
              title={t("emptyTitle")}
              sub={t("emptySub")}
              action={<ButtonLink href="/start" variant="primary">{t("buildFirst")}</ButtonLink>}
            />
          ) : null}

          {plans?.map((p) => (
            <Link key={p.planId} href={`/plan/${encodeURIComponent(p.planId)}`} className="block">
              <Card className="flex items-center justify-between gap-3 p-5 transition-all hover:-translate-y-0.5 hover:shadow-[0_12px_36px_rgba(2,6,12,0.45)]">
                <div className="min-w-0">
                  <h2 className="truncate ds-subtitle-lg text-ink-deep">
                    {p.businessName || p.businessType}
                  </h2>
                  <p className="mt-0.5 text-charcoal ds-body-sm">
                    {formatInr(p.monthlyBudgetInr)} · {p.city}
                    {p.goal && GOAL_LABEL[p.goal] ? ` · ${tW(GOAL_LABEL[p.goal])}` : ""}
                  </p>
                  <p className="mt-0.5 text-steel ds-caption">
                    {t("created")}: {formatDateShort(p.createdAt, p.language === "hi" ? "hi" : "en")}
                  </p>
                </div>
                <span className="shrink-0 text-steel">→</span>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
