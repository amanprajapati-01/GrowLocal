"use client";

import { useTranslations } from "next-intl";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { formatInr } from "@/lib/format";

/** Deterministic data-viz palette (cobalt is only the first slice by size rank, not a rule). */
const SLICE_COLORS = ["#0064e0", "#1876f2", "#31a24c", "#f2a918", "#a121ce", "#5d6c7b"];
const CHART_H = 200;

export type BudgetSlice = { channelId: string; label: string; amount: number };

/** Donut of budgetAllocation.items + a text legend (numbers stay en-IN digits). */
export default function BudgetChart({
  items,
  buffer,
}: {
  items: BudgetSlice[];
  buffer: number;
}) {
  const t = useTranslations("dashboard");
  const tBudget = useTranslations("common");

  const slices = items
    .filter((s) => s.amount > 0)
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 6);

  const hasSlices = slices.length > 0;

  return (
    <div className="flex flex-col items-center gap-4">
      {hasSlices ? (
        <div style={{ height: CHART_H }} className="w-full max-w-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={slices}
                dataKey="amount"
                nameKey="channelId"
                innerRadius="62%"
                outerRadius="95%"
                paddingAngle={2}
                strokeWidth={0}
              >
                {slices.map((_, i) => (
                  <Cell key={i} fill={SLICE_COLORS[i % SLICE_COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="flex h-52 w-52 items-center justify-center rounded-full border-4 border-dashed border-hairline-soft">
          <span className="ds-subtitle-lg text-success">₹0</span>
        </div>
      )}

      <ul className="w-full space-y-1.5" role="list">
        {hasSlices
          ? slices.map((s, i) => (
              <li key={s.channelId} className="flex items-center gap-2 ds-body-sm">
                <span
                  aria-hidden
                  className="inline-block h-3 w-3 shrink-0 rounded-full"
                  style={{ background: SLICE_COLORS[i % SLICE_COLORS.length] }}
                />
                <span className="min-w-0 flex-1 truncate text-ink">{s.label}</span>
                <span className="tabular-nums font-bold text-ink-deep">
                  {formatInr(s.amount)}
                </span>
              </li>
            ))
          : null}
        {buffer > 0 ? (
          <li className="flex items-center gap-2 ds-body-sm">
            <span
              aria-hidden
              className="inline-block h-3 w-3 shrink-0 rounded-full border-2 border-dashed border-steel"
            />
            <span className="min-w-0 flex-1 truncate text-charcoal">{tBudget("buffer")}</span>
            <span className="tabular-nums font-bold text-charcoal">{formatInr(buffer)}</span>
          </li>
        ) : null}
      </ul>

      <p className="w-full text-steel ds-caption">{t("budgetRuleNote")}</p>
    </div>
  );
}
