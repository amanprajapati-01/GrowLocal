"use client";

import { useLocale } from "next-intl";
import { setLocaleCookie, type Locale } from "@/lib/locale";

/** EN / हिं pill toggle — sets the `locale` cookie and reloads (no URL routing). */
export default function LanguageToggle({ className = "" }: { className?: string }) {
  const current: Locale = useLocale() === "hi" ? "hi" : "en";

  const options: Array<{ key: Locale; label: string }> = [
    { key: "en", label: "EN" },
    { key: "hi", label: "हिं" },
  ];

  return (
    <div
      role="group"
      aria-label={current === "hi" ? "भाषा" : "Language"}
      className={`glass-pill inline-flex items-center gap-1 rounded-full p-1 ${className}`}
    >
      {options.map((opt) => {
        const active = opt.key === current;
        return (
          <button
            key={opt.key}
            type="button"
            onClick={() => setLocaleCookie(opt.key)}
            disabled={active}
            className={[
              "h-9 min-w-11 rounded-full px-3 text-body-sm font-bold leading-9 transition-colors",
              active
                ? "glass-active" // pill-tab-active analog on glass
                : "text-ink transition-colors hover:bg-white/10",
            ].join(" ")}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
