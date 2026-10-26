import { getTranslations } from "next-intl/server";
import TopBar from "@/components/TopBar";
import { ButtonLink } from "@/components/Button";
import Card from "@/components/Card";

export default async function Home() {
  const t = await getTranslations("landing");

  const steps = [
    { title: t("how1Title"), sub: t("how1Sub"), emoji: "1️⃣" },
    { title: t("how2Title"), sub: t("how2Sub"), emoji: "2️⃣" },
    { title: t("how3Title"), sub: t("how3Sub"), emoji: "3️⃣" },
  ] as const;

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />

      <main className="mx-auto w-full max-w-6xl flex-1 px-5 pb-24">
        {/* Hero — dark aurora glass panel with glow accents + dual CTA */}
        <section className="glass-hero relative mt-6 overflow-hidden rounded-3xl px-6 py-12 sm:max-w-3xl sm:px-10 sm:py-16">
          <div
            aria-hidden
            className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-[radial-gradient(circle,rgba(0,100,224,0.5),transparent_70%)] blur-2xl"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -bottom-20 -left-10 h-48 w-48 rounded-full bg-[radial-gradient(circle,rgba(161,33,206,0.35),transparent_70%)] blur-2xl"
          />

          <h1 className="relative text-white ds-display">{t("heroTitle")}</h1>
          <p className="relative mt-4 max-w-xl text-white/75 ds-body">{t("heroSub")}</p>
          <div className="relative mt-8 flex flex-wrap items-center gap-3">
            {/* In-app generation flow CTA → cobalt buy-cta with halo per DESIGN.md */}
            <ButtonLink href="/start" variant="buy">
              {t("ctaStart")}
            </ButtonLink>
            <ButtonLink href="/start?prefill=bakery" variant="secondary">
              {t("ctaDemo")}
            </ButtonLink>
          </div>
          <p className="relative mt-8 text-white/55 ds-caption">{t("trustLine")}</p>
        </section>

        {/* How it works — 3-up glass tiles (1-up mobile, 3-up ≥ sm) */}
        <section className="mt-12 sm:mt-16">
          <h2 className="ds-heading text-ink-deep">{t("howTitle")}</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            {steps.map((s) => (
              <Card key={s.title} className="flex flex-col gap-2">
                <span aria-hidden className="text-2xl">{s.emoji}</span>
                <h3 className="ds-subtitle-lg text-ink-deep">{s.title}</h3>
                <p className="text-charcoal ds-body-sm">{s.sub}</p>
              </Card>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
