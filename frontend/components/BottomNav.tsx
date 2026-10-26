"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { Home, NotebookText, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

/** Floating glass pill dock (Home · My plans · New plan) — hidden ≥ 640px. */
export default function BottomNav() {
  const t = useTranslations("nav");
  const pathname = usePathname();

  const items: Array<{ href: string; icon: LucideIcon; label: string }> = [
    { href: "/", icon: Home, label: t("home") },
    { href: "/plans", icon: NotebookText, label: t("myPlans") },
    { href: "/start", icon: Sparkles, label: t("newPlan") },
  ];

  return (
    <nav
      aria-label="primary"
      className="fixed inset-x-4 bottom-3 z-40 sm:hidden"
    >
      <div className="glass-pill mx-auto grid max-w-md grid-cols-3 rounded-full px-2 py-1">
        {items.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={[
                "relative flex h-12 flex-col items-center justify-center gap-0.5 rounded-full ds-caption-bold transition-colors",
                active
                  ? "glass-active"
                  : "text-steel hover:text-ink",
              ].join(" ")}
            >
              <Icon size={18} strokeWidth={active ? 2.4 : 1.8} aria-hidden />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
