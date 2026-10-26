import { getTranslations } from "next-intl/server";
import LanguageToggle from "@/components/LanguageToggle";

export default async function Home() {
  const t = await getTranslations("landing");

  return (
    <main className="mx-auto flex min-h-dvh max-w-6xl flex-col px-5 py-6">
      <header className="flex items-center justify-between">
        <span className="ds-subtitle-lg text-ink-deep">GrowLocal</span>
        <LanguageToggle />
      </header>

      <section className="mt-16 flex flex-col gap-5">
        <h1 className="ds-display text-ink-deep">{t("heroTitle")}</h1>
        <p className="ds-body max-w-xl text-charcoal">{t("heroSub")}</p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <a
            href="/start"
            className="inline-flex h-11 items-center justify-center rounded-full bg-ink-button px-7 text-body-sm font-bold leading-none text-white"
          >
            {t("ctaStart")}
          </a>
          <a
            href="/start"
            className="inline-flex h-11 items-center justify-center rounded-full border-2 border-ink-deep px-6 text-body-sm font-bold leading-none text-ink-deep"
          >
            {t("ctaDemo")}
          </a>
        </div>
      </section>
    </main>
  );
}
