import Link from "next/link";
import { useTranslations } from "next-intl";
import LanguageToggle from "@/components/LanguageToggle";

/** Sticky white top bar: logo · language toggle · sign-in (Appflow S9). */
export default function TopBar() {
  const t = useTranslations("nav");

  return (
    <header className="sticky top-0 z-40 border-b border-hairline-soft bg-canvas">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
        <Link href="/" className="ds-subtitle-lg text-ink-deep" aria-label="GrowLocal">
          GrowLocal
        </Link>
        <div className="flex items-center gap-3">
          <LanguageToggle />
          <Link
            href="/login"
            className="h-10 rounded-full border border-hairline px-4 leading-10 ds-body-sm font-bold text-ink"
          >
            {t("signIn")}
          </Link>
        </div>
      </div>
    </header>
  );
}
