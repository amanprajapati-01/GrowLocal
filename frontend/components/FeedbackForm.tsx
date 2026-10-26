"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useState } from "react";
import Card from "@/components/Card";
import { Button, ButtonLink } from "@/components/Button";
import ErrorState from "@/components/ErrorState";
import { getPlan, getChannels, postFeedback, ApiError, type PlanResponse, type ChannelMeta } from "@/lib/api";
import { useToast } from "@/components/Toast";

const OUTCOMES = [
  { key: "outcomeWorked", value: "worked" },
  { key: "outcomeNeutral", value: "neutral" },
  { key: "outcomeNotWorked", value: "did_not_work" },
] as const;

/** S8 — what worked / didn't; feeds the next plan. */
export default function FeedbackForm({ planId }: { planId: string }) {
  const t = useTranslations("feedback");
  const tCommon = useTranslations("common");
  const { showToast } = useToast();

  const [channels, setChannels] = useState<ChannelMeta[]>([]);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const usedChannelIds = useMemo(() => {
    if (!plan) return ["google_business_profile", "whatsapp_business"];
    return plan.channels.map((c) => c.channelId);
  }, [plan]);

  const [channelId, setChannelId] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<string>("worked");
  const [note, setNote] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const load = useCallback(() => {
    // .then-callbacks are external-system callbacks → effect-safe per react-hooks rules.
    return Promise.all([
      getPlan(planId).catch(() => null),
      getChannels().catch(() => ({ channels: [] })),
    ])
      .then(([planRes, channelsRes]) => {
        setPlan(planRes);
        setChannels(channelsRes.channels ?? []);
        setChannelId(
          (prev) => prev ?? planRes?.channels[0]?.channelId ?? "google_business_profile"
        );
        setError(null);
      })
      .catch(() => {
        setError("generic");
      });
  }, [planId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function submit() {
    if (!channelId || sending) return;
    setSending(true);
    try {
      await postFeedback({
        planId,
        channelId,
        outcome: outcome as "worked" | "neutral" | "did_not_work",
        note: note.trim().slice(0, 200) || undefined,
      });
      setSent(true);
      showToast(t("thanks"));
    } catch (e) {
      setError(e instanceof ApiError && e.code === "network" ? "network" : "generic");
    } finally {
      setSending(false);
    }
  }

  if (error) return <ErrorState code={error} onRetry={() => void load()} />;

  if (sent) {
    return (
      <div className="mx-auto w-full max-w-md px-5 pt-16 text-center">
        <span aria-hidden className="text-4xl">🎉</span>
        <h2 className="mt-3 ds-heading text-ink-deep">{t("thanks")}</h2>
        <div className="mt-6 flex justify-center gap-3">
          <ButtonLink href={`/plan/${planId}`} variant="primary">
            ← {tCommon("back")}
          </ButtonLink>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-5 pb-24">
      <div className="mt-6">
        <h1 className="ds-heading text-ink-deep">{t("title")}</h1>
        <p className="mt-1 text-charcoal ds-body-sm">{t("sub")}</p>
      </div>

      <Card className="mt-6 flex flex-col gap-6">
        <div>
          <span className="ds-caption-bold text-steel">{t("channelLabel")}</span>
          <div className="mt-2 flex flex-wrap gap-2">
            {usedChannelIds.map((id) => {
              const meta = channels.find((c) => c.id === id);
              const name = meta?.name?.en ?? id;
              const active = channelId === id;
              return (
                <button
                  key={id}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setChannelId(id)}
                  className={[
                    "h-10 rounded-full px-4 ds-body-sm font-bold leading-none backdrop-blur-md transition-colors",
                    active
                      ? "glass-active"
                      : "border border-white/16 bg-white/6 text-ink hover:bg-white/12",
                  ].join(" ")}
                >
                  {name}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <span className="ds-caption-bold text-steel">{t("title")}</span>
          <div className="mt-2 grid gap-2 sm:grid-cols-3">
            {OUTCOMES.map((o) => (
              <button
                key={o.key}
                type="button"
                aria-pressed={outcome === o.value}
                onClick={() => setOutcome(o.value)}
                className={[
                  "h-11 rounded-lg px-3 ds-body-sm font-bold transition-[border,box-shadow] duration-150",
                  outcome === o.value
                    ? "border-2 border-selection-glow bg-white/6 text-ink-deep shadow-[0_0_18px_rgba(0,100,224,0.25)]" // aurora selection glow
                    : "border border-white/14 glass-solid text-ink",
                ].join(" ")}
              >
                {t(o.key)}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="fb-note" className="ds-body-sm font-bold text-ink">
            {t("noteLabel")}
          </label>
          <textarea
            id="fb-note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={t("notePlaceholder")}
            rows={3}
            maxLength={200}
            className="field"
          />
        </div>

        <Button variant="buy" size="md" disabled={sending} onClick={() => void submit()}>
          {sending ? t("sending") : t("submit")}
        </Button>
      </Card>
    </div>
  );
}
