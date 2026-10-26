import Link from "next/link";
import { useTranslations } from "next-intl";
import LanguageToggle from "@/components/LanguageToggle";

/** Sticky glass top bar: logo · language toggle · sign-in (Appflow S9). */
export default function TopBar() {
  const t = useTranslations("nav");

  return (
    <header className="sticky top-0 z-40 glass-pill rounded-none border-x-0 border-t-0">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
        <Link href="/" className="ds-subtitle-lg text-white drop-shadow-[0_1px_8px_rgba(77,155,255,0.35)]" aria-label="GrowLocal">
          GrowLocal
        </Link>
        <div className="flex items-center gap-3">
          <LanguageToggle />
          <Link
            href="/login"
            className="h-10 rounded-full border border-white/25 bg-white/8 px-4 leading-10 ds-body-sm font-bold text-ink-deep backdrop-blur-md"
          >
            {t("signIn")}
          </Link>
        </div>
      </div>
    </header>
  );
}
