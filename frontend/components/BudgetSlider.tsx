"use client";

import { useTranslations } from "next-intl";
import { formatInr } from "@/lib/format";

const PRESETS = [0, 1000, 3000, 5000, 10000];
const MAX = 100000;
const STEP = 100;

/** Constraint-controlled range input + preset pills + custom amount (Step 3 of S2-3). */
export default function BudgetSlider({
  value,
  onChange,
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  const t = useTranslations("wizard");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-baseline gap-x-2">
        <span className="ds-display text-ink-deep">{formatInr(value)}</span>
        <span className="ds-body text-steel">{t("budgetCustomLabel")}</span>
      </div>

      <input
        type="range"
        min={0}
        max={MAX}
        step={STEP}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-11 w-full accent-[#1876f2]"
        aria-label={t("budgetLabel")}
      />

      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p) => {
          const selected = value === p;
          return (
            <button
              key={p}
              type="button"
              onClick={() => onChange(p)}
              aria-pressed={selected}
              className={[
                "h-10 rounded-full px-4 ds-body-sm font-bold leading-none transition-colors",
                selected
                  ? "bg-ink-deep text-white"
                  : "border border-hairline bg-canvas text-ink",
              ].join(" ")}
            >
              {p === 10000 ? `${t("preset10k")}+` : formatInr(p)}
            </button>
          );
        })}
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="budget-custom" className="ds-body-sm font-bold text-ink">
          {t("budgetCustomLabel")}
        </label>
        <input
          id="budget-custom"
          type="number"
          inputMode="numeric"
          min={0}
          max={MAX}
          step={STEP}
          value={value}
          onChange={(e) => {
            const n = Number(e.target.value);
            if (Number.isFinite(n)) onChange(Math.min(Math.max(0, Math.round(n)), MAX));
          }}
          className="h-11 rounded-lg border border-hairline bg-canvas px-3 ds-body text-ink focus:border-2 focus:border-fb-blue focus:outline-none"
        />
      </div>

      <p className="text-steel ds-body-sm">{t("budgetHint")}</p>
    </div>
  );
}
