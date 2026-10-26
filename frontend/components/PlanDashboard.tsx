"use client";

import { useLocale, useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useState } from "react";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import ChannelCard from "@/components/ChannelCard";
import BudgetChart, { type BudgetSlice } from "@/components/BudgetChart";
import WeekAccordion from "@/components/WeekAccordion";
import FestivalChip from "@/components/FestivalChip";
import ErrorState from "@/components/ErrorState";
import { Skeleton, SkeletonCard } from "@/components/Skeleton";
import { useToast } from "@/components/Toast";
import { Button, ButtonLink, ButtonExternal } from "@/components/Button";
import {
  getPlan,
  getChannels,
  ApiError,
  taskId,
  type PlanResponse,
  type ChannelMeta,
} from "@/lib/api";

const GOAL_LABEL: Record<string, string> = {
  more_walk_ins: "goal_more_walk_ins",
  online_orders: "goal_online_orders",
  repeat_customers: "goal_repeat_customers",
  brand_awareness: "goal_brand_awareness",
};

export default function PlanDashboard({ planId }: { planId: string }) {
  const locale = useLocale() === "hi" ? "hi" : "en";
  const t = useTranslations("dashboard");
  const tW = useTranslations("wizard");
  const tCommon = useTranslations("common");
  const tPlans = useTranslations("plans");
  const { showToast } = useToast();

  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [channels, setChannels] = useState<ChannelMeta[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const doneMap = useMemo(() => {
    const map: Record<string, boolean> = {};
    plan?.actionPlan.weeks.forEach((w) =>
      w.tasks.forEach((task, i) => {
        map[taskId(w.week, i)] = task.done ?? false;
      })
    );
    return map;
  }, [plan]);

  const load = useCallback(() => {
    // .then-callbacks count as external-system callbacks → effect-safe per react-hooks rules.
    return Promise.all([
      getPlan(planId),
      getChannels().catch(() => ({ channels: [] })),
    ])
      .then(([planRes, channelsRes]) => {
        setPlan(planRes);
        setChannels(channelsRes.channels ?? []);
        setError(null);
        setLoading(false);
      })
      .catch((e: unknown) => {
        const code = e instanceof ApiError ? e.code : "unknown";
        setError(code === "not_found" ? "planNotFound" : code === "network" ? "network" : "generic");
        setLoading(false);
      });
  }, [planId]);

  /** Retry from the UI: explicit transition back to the loading skeleton. */
  const reload = useCallback(() => {
    setLoading(true);
    return load();
  }, [load]);

  useEffect(() => {
    void load();
  }, [load]);

  const metaFor = useCallback(
    (id: string): ChannelMeta | undefined => channels.find((c) => c.id === id),
    [channels]
  );

  const channelName = useCallback(
    (id: string) => {
      const m = metaFor(id);
      if (!m) return id;
      return m.name?.[locale] ?? m.name?.en ?? id;
    },
    [metaFor, locale]
  );

  // ---------- fetch states ----------
  if (loading) return <DashboardSkeleton />;

  if (error || !plan) return <ErrorState code={error ?? "generic"} onRetry={() => void reload()} />;

  const total = plan.budgetAllocation.totalInr;
  const inputs = readStoredInputs();
  const slices: BudgetSlice[] = plan.budgetAllocation.items.map((i) => ({
    channelId: i.channelId,
    label: channelName(i.channelId),
    amount: i.amountInr,
  }));

  const paidRecs = plan.channels;
  const shareText = `${tPlans("budgetLabel", { amount: total.toLocaleString("en-IN") })} · ${window.location.origin}/plan/${plan.planId}`;

  return (
    <div className="mx-auto w-full max-w-3xl px-5 pb-24">
      {/* 1 — Summary header (aurora glass hero) */}
      <section className="glass-hero relative mt-6 overflow-hidden rounded-3xl px-6 py-8 text-white">
        <div
          aria-hidden
          className="pointer-events-none absolute -right-12 -top-12 h-44 w-44 rounded-full bg-[radial-gradient(circle,rgba(0,100,224,0.45),transparent_70%)] blur-2xl"
        />
        <p className="relative ds-caption-bold text-white/60">
          {inputs?.businessName ?? planId} · {t("summaryGoal")}
        </p>
        <h1 className="relative mt-1 ds-heading text-white">
          {tPlans("budgetLabel", { amount: total.toLocaleString("en-IN") })}
          {inputs?.goal ? ` · ${tW(GOAL_LABEL[inputs.goal] ?? "goal_more_walk_ins")}` : ""}
        </h1>
        {inputs?.city ? (
          <p className="relative mt-1 text-white/70 ds-body-sm">{inputs.city}</p>
        ) : null}
        {plan.modelUsed && plan.modelUsed !== "gemini" ? (
          <Badge variant="warning" className="relative mt-3">{t("aiNote")}</Badge>
        ) : null}
      </section>

      {/* 2 — Persona */}
      <section className="mt-6">
        <h2 className="ds-heading text-ink-deep">{t("personaTitle")}</h2>
        <Card className="mt-4 flex flex-col gap-4">
          <div>
            <h3 className="ds-subtitle-lg text-ink-deep">{plan.persona.name}</h3>
            <p className="mt-1 text-charcoal ds-body">{plan.persona.summary}</p>
          </div>
          <p className="text-steel ds-body-sm">{t("personaAge")}: {plan.persona.ageRange}</p>
          <PersonaList title={t("personaWhere")} items={plan.persona.whereTheySpendTime} />
          <PersonaList title={t("personaResponds")} items={plan.persona.whatTheyRespondTo} />
          <PersonaList title={t("personaTriggers")} items={plan.persona.buyingTriggers} />
        </Card>
      </section>

      {/* 3 — Budget split */}
      <section className="mt-10">
        <h2 className="ds-heading text-ink-deep">{t("budgetTitle")}</h2>
        <p className="mt-1 text-charcoal ds-body-sm">
          {t("budgetSub", { total: total.toLocaleString("en-IN") })}
        </p>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <Card className="p-6">
            <BudgetChart items={slices} buffer={plan.budgetAllocation.bufferInr} />
          </Card>
          <div className="flex flex-col gap-3">
            {paidRecs.map((rec) => (
              <ChannelCard key={rec.channelId} meta={metaFor(rec.channelId) ?? fallbackMeta(rec.channelId)} rec={rec} />
            ))}
          </div>
        </div>
      </section>

      {/* 4 — Start free today */}
      {plan.startFreeToday.length ? (
        <section className="mt-10">
          <h2 className="ds-heading text-ink-deep">{t("startFreeTitle")}</h2>
          <p className="mt-1 text-charcoal ds-body-sm">{t("startFreeSub")}</p>
          <ul className="mt-4 flex flex-col gap-3">
            {plan.startFreeToday.map((a, i) => (
              <li key={i}>
                <Card className="flex items-center justify-between gap-3 p-4">
                  <span className="ds-body text-ink-deep">{a.title}</span>
                  <Badge variant="free">{tCommon("minutes", { n: a.minutes })}</Badge>
                </Card>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {/* 5 — 4-week plan */}
      <section className="mt-10">
        <h2 className="ds-heading text-ink-deep">{t("weeksTitle")}</h2>
        <div className="mt-4">
          <WeekAccordion
            planId={plan.planId}
            weeks={plan.actionPlan.weeks}
            doneMap={doneMap}
            channels={channels}
            onPatched={(p) =>
              setPlan((prev) =>
                prev
                  ? {
                      ...prev,
                      actionPlan: {
                        weeks: prev.actionPlan.weeks.map((w) => ({
                          ...w,
                          tasks: w.tasks.map((task, i) =>
                            taskId(w.week, i) === p.taskId ? { ...task, done: p.done } : task
                          ),
                        })),
                      },
                    }
                  : prev
              )
            }
          />
        </div>
      </section>

      {/* 6 — Festivals */}
      {plan.festivals.length ? (
        <section className="mt-10">
          <h2 className="ds-heading text-ink-deep">
            {t("festivalTitle", { city: inputs?.city ?? "" })}
          </h2>
          <p className="mt-1 text-charcoal ds-body-sm">
            {t("festivalSub")} · <span className="text-attention">{t("festivalVerifyNote")}</span>
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {plan.festivals.map((f) => (
              <FestivalChip key={f.name} festival={f} city={inputs?.city} />
            ))}
          </div>
        </section>
      ) : null}

      {/* Disclaimer */}
      <p className="mt-10 border-t border-hairline-soft pt-4 text-steel ds-caption">
        {plan.disclaimer}
      </p>

      {/* 8 — CTA bar */}
      <section className="glass my-10 rounded-3xl p-6">
        <h2 className="ds-subtitle-lg text-ink-deep">{t("shareTitle")}</h2>
        <div className="mt-4 flex flex-col gap-3">
          <ButtonLink href={`/plan/${plan.planId}/content`} variant="buy" className="w-full sm:w-auto">
            {t("openContent")}
          </ButtonLink>
          <div className="flex flex-wrap gap-3">
            <ButtonExternal href={`https://wa.me/?text=${encodeURIComponent(shareText)}`} variant="secondary" size="sm">
              {t("shareWhatsApp")}
            </ButtonExternal>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                void navigator.clipboard
                  .writeText(`${window.location.origin}/plan/${plan.planId}`)
                  .then(() => showToast(t("linkCopied")))
                  .catch(() => undefined);
              }}
            >
              {t("copyLink")}
            </Button>
            <ButtonLink href={`/plan/${plan.planId}/feedback`} variant="ghost" size="sm">
              {t("giveFeedback")}
            </ButtonLink>
          </div>
          <p className="text-steel ds-caption">{t("guestNote")}</p>
        </div>
      </section>
    </div>
  );
}

function PersonaList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <span className="ds-caption-bold text-steel">{title}</span>
      <ul className="mt-1 flex flex-wrap gap-2">
        {items.map((x, i) => (
          <li key={i} className="rounded-full border border-white/16 bg-white/6 px-3 py-1 ds-body-sm text-ink">
            {x}
          </li>
        ))}
      </ul>
    </div>
  );
}

function DashboardSkeleton() {
  const t = useTranslations("common");
  return (
    <div className="mx-auto w-full max-w-3xl px-5 pb-24">
      <Skeleton className="mt-6 h-28 rounded-3xl" />
      <div className="mt-10 space-y-4">
        {[0, 1, 2].map((i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <p className="mt-6 text-center text-steel ds-caption">{t("loading")}</p>
    </div>
  );
}

function fallbackMeta(id: string): ChannelMeta {
  return { id, name: { en: id, hi: id }, costType: "paid", effort: "", timeToResult: "" };
}

type StoredInputs = { businessName?: string; city?: string; goal?: string };
function readStoredInputs(): StoredInputs | null {
  try {
    const raw = sessionStorage.getItem("growlocal.planRequest");
    if (!raw) return null;
    const p = JSON.parse(raw) as StoredInputs;
    return p;
  } catch {
    return null;
  }
}
