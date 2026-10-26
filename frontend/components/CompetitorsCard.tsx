"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import Card from "@/components/Card";
import { Button } from "@/components/Button";
import { getCompetitors, ApiError, type Competitor } from "@/lib/api";

/** businessType → Google Places includedTypes (best effort; "" = no type filter). */
const PLACE_TYPE: Record<string, string> = {
  bakery: "bakery",
  salon: "beauty_salon",
  restaurant: "restaurant",
  kirana: "supermarket",
  clinic: "doctor",
};

type ViewState =
  | "idle"
  | "locating"
  | "loading"
  | "list"
  | "empty"
  | "denied"
  | "error";

/**
 * Competitor snapshot (P1): device location → GET /api/places.
 * Everything degrades gracefully: no permission / no key / no results → honest empty state.
 */
export default function CompetitorsCard({ businessType }: { businessType: string }) {
  const t = useTranslations("dashboard");
  const [view, setView] = useState<ViewState>("idle");
  const [items, setItems] = useState<Competitor[]>([]);
  const [note, setNote] = useState("");
  const [radius, setRadius] = useState(0);

  function checkNearby() {
    if (!("geolocation" in navigator)) {
      setView("denied");
      return;
    }
    setView("locating");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setView("loading");
        getCompetitors(
          pos.coords.latitude,
          pos.coords.longitude,
          PLACE_TYPE[businessType] ?? ""
        )
          .then((res) => {
            setItems(res.competitors);
            setNote(res.note ?? "");
            setRadius(res.radiusMeters ?? 0);
            setView(res.competitors.length ? "list" : "empty");
          })
          .catch((e: unknown) => {
            // a Places "not configured" note still returns 200 — treat hard errors separately
            if (e instanceof ApiError && e.code === "network") {
              setView("error");
            } else {
              setView("empty");
              setNote(t("competitorsUnavailable"));
            }
          });
      },
      () => setView("denied"),
      { timeout: 10000, maximumAge: 300000 }
    );
  }

  return (
    <Card className="mt-10 flex flex-col gap-3">
      <h3 className="ds-subtitle-lg text-ink-deep">{t("competitorsTitle")}</h3>
      <p className="text-charcoal ds-body-sm">{t("competitorsSub")}</p>

      {view === "idle" ? (
        <Button variant="secondary" size="sm" onClick={checkNearby}>
          {t("competitorsButton")}
        </Button>
      ) : null}

      {view === "locating" || view === "loading" ? (
        <p className="text-steel ds-body-sm" role="status">
          {view === "locating" ? t("competitorsLocating") : t("competitorsLoading")}
        </p>
      ) : null}

      {view === "denied" ? (
        <p className="text-attention ds-body-sm">{t("competitorsDenied")}</p>
      ) : null}

      {view === "error" ? <p className="text-critical-strong ds-body-sm">{t("competitorsUnavailable")}</p> : null}

      {view === "empty" ? (
        <div className="flex flex-col gap-2">
          <p className="text-steel ds-body-sm">{t("competitorsEmpty")}</p>
          {note ? <p className="text-steel ds-caption">{note}</p> : null}
        </div>
      ) : null}

      {view === "list" ? (
        <div className="flex flex-col gap-2">
          <p className="text-steel ds-caption">
            {t("competitorsFound", { n: items.length })} · {t("competitorsRadius", { m: radius })}
          </p>
          <ul className="flex flex-col gap-2">
            {items.map((c, i) => (
              <li
                key={i}
                className="flex items-center justify-between gap-3 rounded-lg border border-white/14 glass-solid px-4 py-2.5"
              >
                <div className="min-w-0">
                  <p className="truncate ds-body-sm font-bold text-ink-deep">{c.name}</p>
                  <p className="truncate text-steel ds-caption">{c.address}</p>
                </div>
                <span className="shrink-0 text-attention ds-body-sm font-bold">
                  ★ {c.rating > 0 ? c.rating.toFixed(1) : "—"}
                  {c.reviewCount ? ` · ${c.reviewCount}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </Card>
  );
}
