"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { Home, NotebookText, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

/** Mobile bottom nav (Home · My plans · New plan) — hidden ≥ 640px per Appflow. */
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
      aria-label={t("home")}
      className="fixed inset-x-0 bottom-0 z-40 border-t border-hairline-soft bg-canvas pb-[env(safe-area-inset-bottom)] sm:hidden"
    >
      <div className="mx-auto grid max-w-md grid-cols-3">
        {items.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={[
                "flex h-14 flex-col items-center justify-center gap-0.5 ds-caption-bold",
                active ? "text-ink-deep" : "text-steel",
              ].join(" ")}
            >
              <Icon size={20} strokeWidth={active ? 2.4 : 1.8} aria-hidden />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
