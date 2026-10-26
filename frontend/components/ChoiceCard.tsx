"use client";

/** radio-option / radio-option-selected — selection borders use 2px #0143b5. */
export default function ChoiceCard({
  selected,
  onSelect,
  title,
  detail,
  emoji,
  name,
}: {
  selected: boolean;
  onSelect: () => void;
  title: string;
  detail?: string;
  emoji?: string;
  name: string;
}) {
  return (
    <div
      role="radio"
      aria-checked={selected}
      tabIndex={0}
      onClick={() => onSelect()}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect();
        }
      }}
      className={[
        "cursor-pointer rounded-lg bg-transparent p-5 ds-body transition-[border,box-shadow] duration-150",
        selected
          ? "border-2 border-selection-glow shadow-[0_0_0_1px_rgba(1,67,181,0.4),0_0_22px_rgba(0,100,224,0.3)]" // radio-option-selected, aurora glow
          : "border border-white/14 glass-solid", // radio-option on dark
      ].join(" ")}
      data-name={name}
    >
      <div className="flex items-center gap-3">
        {emoji ? <span aria-hidden className="text-xl">{emoji}</span> : null}
        <span className="font-bold text-ink-deep">{title}</span>
      </div>
      {detail ? <p className="mt-1 text-charcoal ds-body-sm">{detail}</p> : null}
    </div>
  );
}
