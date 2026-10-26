"use client";

import { useLocale, useTranslations } from "next-intl";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import type { ChannelMeta, ChannelRecommendation } from "@/lib/api";
import { formatInr, formatInrRange } from "@/lib/format";

/** Channel tile: bilingual name, FREE badge or ₹, why + expected range + steps. */
export default function ChannelCard({
  meta,
  rec,
}: {
  meta: ChannelMeta;
  rec?: ChannelRecommendation;
}) {
  const locale = useLocale() === "hi" ? "hi" : "en";
  const t = useTranslations("dashboard");
  const tCommon = useTranslations("common");

  const name = meta.name?.[locale] ?? meta.name?.en ?? meta.id;
  const allocated = rec?.budgetInr ?? 0;
  const paid = meta.costType === "paid" && allocated > 0;

  return (
    <Card className="flex flex-col gap-3 p-6">
      <div className="flex items-start justify-between gap-3">
        <h3 className="ds-subtitle-lg text-ink-deep">{name}</h3>
        {paid ? (
          <Badge variant="warning">{formatInr(allocated)}</Badge>
        ) : rec?.score ? (
          <Badge variant="free">{`⭐ ${tCommon("free")} · ${rec.score}`}</Badge>
        ) : (
          <Badge variant="free">{`⭐ ${tCommon("free")}`}</Badge>
        )}
      </div>

      {rec ? (
        <>
          <p className="text-charcoal ds-body-sm">{rec.rationale}</p>
          <div className="flex flex-col gap-1">
            <span className="ds-caption-bold text-steel">{t("expectedResult")}</span>
            <p className="text-ink ds-body-sm">{rec.expectedResult}</p>
          </div>
          <div className="flex flex-col gap-1">
            <span className="ds-caption-bold text-steel">{t("howToStart")}</span>
            <ol className="flex flex-col gap-1 text-charcoal ds-body-sm">
              {rec.howToStart.map((step, i) => (
                <li key={i} className="flex gap-2">
                  <span aria-hidden className="text-steel">{i + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </>
      ) : (
        <p className="text-charcoal ds-body-sm">
          {locale === "hi" ? "प्रयास: " : "Effort: "}
          {meta.effort} · {locale === "hi" ? "असर दिखेगा " : "Results in "}
          {meta.timeToResult}
        </p>
      )}
    </Card>
  );
}

/** Est-range helper re-exported so charts stay consistent. */
export function estLabel(lo: number, hi: number) {
  return formatInrRange(lo, hi);
}
