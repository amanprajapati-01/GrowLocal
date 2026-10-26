"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import ContentCard, { type ContentCardItem } from "@/components/ContentCard";
import ErrorState from "@/components/ErrorState";
import { SkeletonCard } from "@/components/Skeleton";
import { postContent, ApiError, type ContentPack } from "@/lib/api";

const TAB_TYPES = [
  { key: "whatsapp", label: "tabWhatsapp" },
  { key: "instagram", label: "tabInstagram" },
  { key: "gbp_post", label: "tabGbp" },
  { key: "offer", label: "tabOffers" },
] as const;

type Props = { planId: string; language: "en" | "hi" };

type TabKey = "whatsapp" | "instagram" | "gbp_post" | "offer";

/** Map a typed ContentPack into per-tab card items. */
function packToItems(pack: ContentPack): Record<string, ContentCardItem[]> {
  const items: Record<string, ContentCardItem[]> = {
    whatsapp: pack.whatsapp.map((w) => ({
      channelId: "whatsapp_business",
      type: "whatsapp",
      title: w.label,
      body: w.text,
    })),
    instagram: pack.instagram.map((ig) => ({
      channelId: "instagram_organic",
      type: "instagram",
      body: ig.caption,
      hashtags: ig.hashtags,
      reelIdea: ig.reelIdea,
    })),
    gbp_post: pack.gbpPost
      ? [
          {
            channelId: "google_business_profile",
            type: "gbp_post",
            title: pack.gbpPost.title,
            body: pack.gbpPost.body,
            ctaType: pack.gbpPost.ctaType,
          },
        ]
      : [],
    offer: pack.offers.map((o) => ({
      channelId: "offer_flyer",
      type: "offer",
      title: o.name,
      body: o.description,
      validityDays: o.validityDays,
    })),
  };
  return items;
}

export default function ContentStudio({ planId, language }: Props) {
  const t = useTranslations("content");
  const tCommon = useTranslations("common");
  const [tab, setTab] = useState<TabKey>("whatsapp");
  const [pack, setPack] = useState<ContentPack | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenType, setRegenType] = useState<string | null>(null);

  const items = pack ? packToItems(pack) : null;

  const load = useCallback(() => {
    // .then-callbacks are external-system callbacks → effect-safe per react-hooks rules.
    return postContent(planId, language)
      .then((res) => {
        setPack(res);
        setError(null);
        setLoading(false);
      })
      .catch((e: unknown) => {
        setError(
          e instanceof ApiError ? (e.code === "not_found" ? "planNotFound" : "generic") : "network"
        );
        setLoading(false);
      });
  }, [planId, language]);

  useEffect(() => {
    void load();
  }, [load]);

  async function regenerate(type: TabKey) {
    setRegenType(type);
    try {
      // Backend caches packs; a type-scoped POST reuses the cache for MVP.
      const res = await postContent(planId, language, [type]);
      setPack(res);
    } catch {
      /* keep the old pack on failure */
    } finally {
      setRegenType(null);
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-5 pb-24">
      <div className="mt-6">
        <h1 className="ds-heading text-ink-deep">{t("title")}</h1>
        <p className="mt-1 text-charcoal ds-body-sm">{t("sub")}</p>
        <p className="mt-2 text-attention ds-caption-bold">⚠ {t("aiNote")}</p>
      </div>

      {/* pill tabs */}
      <div className="mt-6 flex flex-wrap gap-2" role="tablist" aria-label={t("title")}>
        {TAB_TYPES.map((x) => (
          <button
            key={x.key}
            type="button"
            role="tab"
            aria-selected={tab === x.key}
            onClick={() => setTab(x.key)}
            className={[
              "h-10 rounded-full px-4 ds-body-sm font-bold leading-none backdrop-blur-md transition-colors",
              tab === x.key
                ? "glass-active"
                : "border border-white/16 bg-white/6 text-ink hover:bg-white/12",
            ].join(" ")}
          >
            {t(x.label)}
          </button>
        ))}
        <button
          type="button"
          onClick={() => void regenerate(tab)}
          className="h-10 rounded-full border border-white/14 bg-white/4 px-4 ds-body-sm font-bold text-ink-deep backdrop-blur-sm hover:bg-white/10"
        >
          {tCommon("regenerate")}
        </button>
      </div>

      <div className="mt-6 flex flex-col gap-4">
        {loading ? (
          [0, 1].map((i) => <SkeletonCard key={i} />)
        ) : error ? (
          <ErrorState code={error} onRetry={() => void load()} />
        ) : items && items[tab]?.length ? (
          items[tab].map((item, i) => (
            <ContentCard
              key={`${tab}-${i}`}
              item={item}
              onRegenerate={() => regenerate(tab)}
              regenerating={regenType === tab}
            />
          ))
        ) : (
          <div className="glass rounded-xl p-8 text-center">
            <p className="ds-subtitle-lg text-ink-deep">{t("emptyTitle")}</p>
            <p className="mt-1 text-charcoal ds-body-sm">{t("emptySub")}</p>
          </div>
        )}
      </div>
    </div>
  );
}
