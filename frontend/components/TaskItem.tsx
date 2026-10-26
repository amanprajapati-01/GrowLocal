"use client";

import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";
import type { ChannelMeta, Task } from "@/lib/api";
import { formatInr } from "@/lib/format";

/** One checkable plan task; PATCHes done state optimistically. */
export default function TaskItem({
  planId,
  week,
  index,
  task,
  done,
  channels,
  onPatched,
}: {
  planId: string;
  week: number;
  index: number; // 0-based positional index within the week
  task: Task;
  done: boolean;
  channels: ChannelMeta[];
  onPatched?: (patched: { planId: string; taskId: string; done: boolean }) => void;
}) {
  const locale = useLocale() === "hi" ? "hi" : "en";
  const tDash = useTranslations("dashboard");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [optimistic, setOptimistic] = useState<boolean | null>(null);
  const [error, setError] = useState(false);

  const checked = optimistic ?? done;

  function channelName(channelId: string): string {
    const meta = channels.find((c) => c.id === channelId);
    if (!meta) return channelId;
    return meta.name?.[locale] ?? meta.name?.en ?? channelId;
  }

  async function toggle() {
    const next = !checked;
    setOptimistic(next);
    setError(false);
    try {
      const { patchTask, taskId } = await import("@/lib/api");
      const id = task.id ?? taskId(week, index);
      await patchTask(planId, id, next);
      onPatched?.({ planId, taskId: id, done: next });
    } catch {
      setError(true);
      setOptimistic(null); // rollback
    }
  }

  return (
    <div
      className={[
        "flex items-start gap-3 rounded-lg border p-3 transition-colors duration-150",
        checked ? "border-success/40 bg-surface-soft" : "border-hairline-soft bg-canvas",
      ].join(" ")}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={toggle}
        aria-label={checked ? tDash("taskDone") : tDash("markDone")}
        className="mt-0.5 h-5 w-5 shrink-0 cursor-pointer accent-[#1876f2]"
      />
      <div className="min-w-0 flex-1">
        <p className={`ds-body ${checked ? "text-stone line-through" : "text-ink-deep"}`}>
          {task.title}
        </p>
        <p className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 ds-caption text-steel">
          {channelName(task.channelId)}
          <span>· {tCommon("minutes", { n: task.minutes })}</span>
          {task.costInr > 0 ? (
            <span>
              · {formatInr(task.costInr)} ({tCommon("estLabel")})
            </span>
          ) : (
            <span>· {tCommon("free")}</span>
          )}
        </p>
        {error ? <p className="mt-1 ds-caption-bold text-critical-strong">{tErrors("network")}</p> : null}
      </div>
    </div>
  );
}
