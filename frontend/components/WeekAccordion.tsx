"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import type { ChannelMeta, Week } from "@/lib/api";
import TaskItem from "@/components/TaskItem";
import Card from "@/components/Card";

/** faq-accordion-item chrome — one Week per item; Week 1 open by default. */
export default function WeekAccordion({
  planId,
  weeks,
  doneMap,
  channels,
  onPatched,
}: {
  planId: string;
  weeks: Week[];
  doneMap: Record<string, boolean>; // taskId -> done (from plan doc refs)
  channels: ChannelMeta[];
  onPatched?: (patched: { taskId: string; done: boolean }) => void;
}) {
  const t = useTranslations("dashboard");
  const [open, setOpen] = useState<number>(weeks[0]?.week ?? 1);

  return (
    <div className="flex flex-col gap-3">
      {weeks.map((week) => {
        const expanded = open === week.week;
        return (
          <Card key={week.week} className="overflow-hidden p-0">
            <button
              type="button"
              onClick={() => setOpen(expanded ? 0 : week.week)}
              aria-expanded={expanded}
              className="flex w-full items-center justify-between gap-3 bg-canvas p-6 text-left"
            >
              <span className="flex min-w-0 flex-col gap-1">
                <span className="ds-subtitle-lg text-ink-deep">
                  {t("weekLabel", { n: week.week })}
                </span>
                <span className="truncate text-charcoal ds-body-sm">{week.theme}</span>
              </span>
              <span
                aria-hidden
                className={`shrink-0 text-steel transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </span>
            </button>

            {expanded ? (
              <div className="flex flex-col gap-2 border-t border-hairline-soft p-6 pt-4">
                {week.tasks.map((task, i) => (
                  <TaskItem
                    key={`${week.week}-${i}`}
                    planId={planId}
                    week={week.week}
                    index={i}
                    task={task}
                    done={doneMap[`t_w${week.week}_n${i}`] ?? task.done ?? false}
                    channels={channels}
                    onPatched={(p) => onPatched?.(p)}
                  />
                ))}
              </div>
            ) : null}
          </Card>
        );
      })}
    </div>
  );
}
