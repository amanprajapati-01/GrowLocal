"use client";

import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import TopBar from "@/components/TopBar";
import StepperProgress from "@/components/StepperProgress";
import ChoiceCard from "@/components/ChoiceCard";
import Chip from "@/components/Chip";
import BudgetSlider from "@/components/BudgetSlider";
import { Button } from "@/components/Button";
import type { PlanInput } from "@/lib/api";

const TOTAL = 5;

const BUSINESS_TYPES = [
  { id: "kirana", emoji: "🛒" },
  { id: "bakery", emoji: "🥐" },
  { id: "restaurant", emoji: "🍛" },
  { id: "salon", emoji: "💇" },
  { id: "coaching", emoji: "📚" },
  { id: "clinic", emoji: "🩺" },
  { id: "retail", emoji: "👗" },
] as const;

const GOALS = [
  "more_walk_ins",
  "online_orders",
  "repeat_customers",
  "brand_awareness",
] as const;

const AUDIENCES = [
  "families",
  "students",
  "professionals",
  "women",
  "seniors",
  "tourists",
] as const;

const BUSINESS_TYPE_IDS = new Set<string>(BUSINESS_TYPES.map((b) => b.id));

type Draft = PlanInput & {
  otherDescription: string;
};

/** S3 onboarding — one question per screen; answers preserved on back. */
export default function StartPage() {
  const t = useTranslations("wizard");
  const tCommon = useTranslations("common");
  const locale = useLocale() === "hi" ? "hi" : "en";
  const router = useRouter();
  const searchParams = useSearchParams();
  const prefill = searchParams.get("prefill"); // demo shortcut: ?prefill=bakery

  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [draft, setDraft] = useState<Draft>(() => {
    const base: Draft = {
      businessType: "bakery",
      businessName: "",
      city: "",
      locality: "",
      monthlyBudgetInr: 3000,
      goal: "more_walk_ins",
      targetAudience: ["families"],
      targetAudienceText: "",
      language: locale as PlanInput["language"],
      otherDescription: "",
    };
    if (prefill && BUSINESS_TYPE_IDS.has(prefill)) {
      return {
        ...base,
        businessType: prefill,
        businessName: "Sharma Bakery",
        city: "Kanpur",
        locality: "Swaroop Nagar",
      };
    }
    return base;
  });

  function patch(p: Partial<Draft>) {
    setDraft((d) => ({ ...d, ...p }));
  }

  const canNext = useMemo(() => {
    switch (step) {
      case 1:
        if (draft.businessType === "other") {
          return draft.otherDescription.trim().length >= 2;
        }
        return true;
      case 2:
        return draft.city.trim().length >= 2 && draft.locality.trim().length >= 2;
      case 3:
        return draft.monthlyBudgetInr >= 0;
      case 4:
        return Boolean(draft.goal);
      case 5:
        return draft.targetAudience.length >= 1;
      default:
        return true;
    }
  }, [step, draft]);

  /** The `other` free-text rides along as targetAudienceText (backend accepts ≤200 chars). */
  async function submit() {
    if (submitting) return;
    setSubmitting(true);
    const businessName =
      draft.businessName.trim() ||
      (draft.businessType === "other"
        ? draft.otherDescription.trim().slice(0, 60)
        : draft.businessType);
    const targetAudienceText =
      draft.businessType === "other" && !draft.targetAudienceText
        ? draft.otherDescription.trim().slice(0, 200)
        : draft.targetAudienceText;

    const payload: PlanInput & { businessName: string } = {
      ...draft,
      businessName,
      targetAudienceText,
      language: locale as PlanInput["language"],
    };

    try {
      sessionStorage.setItem("growlocal.planRequest", JSON.stringify(payload));
      router.push("/generating");
    } catch {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />

      <main className="mx-auto w-full max-w-2xl flex-1 px-5 pb-32">
        <div className="mt-8">
          <StepperProgress current={step} total={TOTAL} />
          <h1 className="mt-4 ds-heading text-ink-deep">{t("title")}</h1>
        </div>

        <section className="mt-8 flex flex-col gap-6">
          {step === 1 ? (
            <>
              <h2 className="ds-subtitle-lg text-ink">{t("businessLabel")}</h2>
              <div className="grid gap-3 sm:grid-cols-2">
                {BUSINESS_TYPES.map((bt) => (
                  <ChoiceCard
                    key={bt.id}
                    name={bt.id}
                    selected={draft.businessType === bt.id}
                    onSelect={() => patch({ businessType: bt.id })}
                    title={t(`businessType_${bt.id}`)}
                    emoji={bt.emoji}
                  />
                ))}
                <ChoiceCard
                  name="other"
                  selected={draft.businessType === "other"}
                  onSelect={() => patch({ businessType: "other" })}
                  title={t("businessType_other")}
                  emoji="🏪"
                />
              </div>
              {draft.businessType === "other" ? (
                <div className="flex flex-col gap-1">
                  <label htmlFor="other-desc" className="ds-body-sm font-bold text-ink">
                    {t("otherDescLabel")}
                  </label>
                  <input
                    id="other-desc"
                    value={draft.otherDescription}
                    onChange={(e) => patch({ otherDescription: e.target.value })}
                    placeholder={t("otherDescPlaceholder")}
                    maxLength={120}
                    className="field"
                  />
                </div>
              ) : null}
            </>
          ) : null}

          {step === 2 ? (
            <>
              <h2 className="ds-subtitle-lg text-ink">{t("cityLabel")}</h2>
              <div className="flex flex-col gap-4">
                <input
                  autoFocus
                  value={draft.city}
                  onChange={(e) => patch({ city: e.target.value })}
                  placeholder={t("cityPlaceholder")}
                  maxLength={40}
                  aria-label={t("cityLabel")}
                  className="field"
                />
                <label
                  htmlFor="locality"
                  className="ds-body-sm font-bold text-ink"
                >
                  {t("localityLabel")}
                </label>
                <input
                  id="locality"
                  value={draft.locality}
                  onChange={(e) => patch({ locality: e.target.value })}
                  placeholder={t("localityPlaceholder")}
                  maxLength={40}
                  className="field"
                />
              </div>
            </>
          ) : null}

          {step === 3 ? (
            <>
              <h2 className="ds-subtitle-lg text-ink">{t("budgetLabel")}</h2>
              <BudgetSlider
                value={draft.monthlyBudgetInr}
                onChange={(v) => patch({ monthlyBudgetInr: v })}
              />
            </>
          ) : null}

          {step === 4 ? (
            <>
              <h2 className="ds-subtitle-lg text-ink">{t("goalLabel")}</h2>
              <div className="flex flex-col gap-3">
                {GOALS.map((g) => (
                  <ChoiceCard
                    key={g}
                    name={g}
                    selected={draft.goal === g}
                    onSelect={() => patch({ goal: g })}
                    title={t(`goal_${g}`)}
                  />
                ))}
              </div>
            </>
          ) : null}

          {step === 5 ? (
            <>
              <h2 className="ds-subtitle-lg text-ink">{t("audienceLabel")}</h2>
              <div className="flex flex-wrap gap-2">
                {AUDIENCES.map((a) => (
                  <Chip
                    key={a}
                    selected={draft.targetAudience.includes(a)}
                    onClick={() =>
                      patch({
                        targetAudience: draft.targetAudience.includes(a)
                          ? draft.targetAudience.filter((x) => x !== a)
                          : [...draft.targetAudience, a],
                      })
                    }
                  >
                    {t(`audience_${a}`)}
                  </Chip>
                ))}
              </div>
              <div className="flex flex-col gap-1">
                <label htmlFor="audience-text" className="ds-body-sm font-bold text-ink">
                  {t("audienceTextLabel")}
                </label>
                <input
                  id="audience-text"
                  value={draft.targetAudienceText}
                  onChange={(e) => patch({ targetAudienceText: e.target.value })}
                  placeholder={t("audienceTextPlaceholder")}
                  maxLength={200}
                  className="field"
                />
              </div>
            </>
          ) : null}
        </section>
      </main>

      {/* Sticky glass action bar: back + next/build */}
      <div className="fixed inset-x-0 bottom-14 z-30 glass-pill rounded-none border-x-0 border-b-0 sm:bottom-0">
        <div className="mx-auto flex max-w-2xl items-center justify-between gap-3 px-5 py-3">
          {step > 1 ? (
            <Button variant="ghost" size="sm" onClick={() => setStep((s) => s - 1)}>
              {tCommon("back")}
            </Button>
          ) : (
            <Link href="/" className="rounded-full px-4 py-2 ds-body-sm font-bold text-steel">
              {tCommon("back")}
            </Link>
          )}

          {step < TOTAL ? (
            <Button variant="primary" size="sm" disabled={!canNext} onClick={() => setStep((s) => s + 1)}>
              {tCommon("next")}
            </Button>
          ) : (
            <Button variant="buy" size="md" disabled={!canNext || submitting} onClick={() => void submit()}>
              {submitting ? t("building") : t("ctaBuild")}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
