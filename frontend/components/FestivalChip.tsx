"use client";

import { useTranslations } from "next-intl";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import { formatDateShort } from "@/lib/format";
import type { FestivalSuggestion } from "@/lib/api";

/** Compact festival row: name + date pill + suggested offer. */
export default function FestivalChip({
  festival,
  city,
}: {
  festival: FestivalSuggestion;
  city?: string;
}) {
  const t = useTranslations("dashboard");
  const dateLabel = formatDateShort(festival.date, city && /[\u0900-\u097F]/.test(city) ? "hi" : "en");

  return (
    <Card className="flex flex-col gap-2 p-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="ds-subtitle-lg text-ink-deep">{festival.name}</span>
        <Badge variant="warning">{dateLabel}</Badge>
      </div>
      <p className="text-charcoal ds-body-sm">
        <span className="font-bold text-ink">{t("festivalOffer")}: </span>
        {festival.suggestedOffer}
      </p>
    </Card>
  );
}
