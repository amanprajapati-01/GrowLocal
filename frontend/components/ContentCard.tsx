"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { useToast } from "@/components/Toast";
import Card from "@/components/Card";
import Badge from "@/components/Badge";

export type ContentCardItem = {
  channelId: string;
  type: string; // whatsapp | instagram | gbp_post | offer
  title?: string;
  body: string;
  hashtags?: string[];
  reelIdea?: string;
  ctaType?: string;
  validityDays?: number;
  deepLink?: string; // e.g. https://wa.me/?text=...
};

type Props = {
  item: ContentCardItem;
  onRegenerate?: () => Promise<void>;
  regenerating?: boolean;
};

const TYPE_LABELS: Record<string, string> = {
  whatsapp: "tabWhatsapp",
  instagram: "tabInstagram",
  gbp_post: "tabGbp",
  offer: "tabOffers",
};

/** Copyable single content item + regenerate + wa.me deep link. */
export default function ContentCard({ item, onRegenerate, regenerating }: Props) {
  const t = useTranslations("content");
  const tCommon = useTranslations("common");
  const { showToast } = useToast();
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(item.body);
      setCopied(true);
      showToast(tCommon("copied"));
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  }

  const waLink =
    item.deepLink ??
    (item.type === "whatsapp"
      ? `https://wa.me/?text=${encodeURIComponent(item.body)}`
      : undefined);

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1.5">
          <Badge variant="neutral">{t(TYPE_LABELS[item.type] ?? "tabWhatsapp")}</Badge>
          {item.title ? (
            <h3 className="ds-subtitle-lg text-ink-deep">{item.title}</h3>
          ) : null}
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {onRegenerate ? (
            <button
              type="button"
              onClick={() => void onRegenerate()}
              disabled={regenerating}
              className="rounded-full border border-white/14 bg-white/4 px-4 py-2 ds-caption-bold text-ink-deep backdrop-blur-sm hover:bg-white/10 disabled:opacity-60"
            >
              {regenerating ? tCommon("regenerating") : tCommon("regenerate")}
            </button>
          ) : null}
          <button
            type="button"
            onClick={() => void copy()}
            className="rounded-full border border-white/16 bg-white/6 px-4 py-2 ds-caption-bold text-ink backdrop-blur-md hover:bg-white/12"
          >
            {copied ? tCommon("copied") : tCommon("copy")}
          </button>
        </div>
      </div>

      <p className="whitespace-pre-wrap text-ink ds-body">{item.body}</p>

      {item.hashtags?.length ? (
        <p className="ds-body-sm text-primary-soft">{item.hashtags.join(" ")}</p>
      ) : null}
      {item.reelIdea ? (
        <p className="text-charcoal ds-body-sm">
          <span className="font-bold">{t("reelIdeaLabel")}: </span>
          {item.reelIdea}
        </p>
      ) : null}
      {item.validityDays ? (
        <Badge variant="warning">{t("offerValid", { n: item.validityDays })}</Badge>
      ) : null}
      {waLink ? (
        <a
          href={waLink}
          target="_blank"
          rel="noopener noreferrer"
          className="self-start rounded-full bg-[#25d366] px-5 py-2.5 ds-body-sm font-bold text-white"
        >
          {t("openWhatsApp")}
        </a>
      ) : null}
    </Card>
  );
}
