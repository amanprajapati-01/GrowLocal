import { getTranslations } from "next-intl/server";
import { ButtonLink } from "@/components/Button";

/** Friendly 404 — never a raw Next not-found. */
export default async function NotFound() {
  const t = await getTranslations("errors");
  const tHome = await getTranslations("nav");

  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col items-center justify-center gap-4 px-5 text-center">
      <span aria-hidden className="text-4xl">∩_∩</span>
      <h1 className="ds-heading text-ink-deep">{t("notFound")}</h1>
      <p className="text-charcoal ds-body">{t("generic")}</p>
      <ButtonLink href="/" variant="primary">
        {tHome("home")}
      </ButtonLink>
    </main>
  );
}
