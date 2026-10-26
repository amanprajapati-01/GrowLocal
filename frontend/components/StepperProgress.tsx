import { useTranslations } from "next-intl";

/** Progress bar + "Step {current} of {total}" label at the top of the wizard. */
export default function StepperProgress({
  current,
  total,
}: {
  current: number; // 1-based
  total: number;
}) {
  const t = useTranslations("common");
  const pct = Math.round((current / total) * 100);

  return (
    <div className="flex flex-col gap-2" aria-label={t("stepsLabel", { current, total })}>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-hairline-soft">
        <div
          className="h-full rounded-full bg-ink-deep transition-[width] duration-200 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="ds-caption-bold text-steel">{t("stepsLabel", { current, total })}</span>
    </div>
  );
}
