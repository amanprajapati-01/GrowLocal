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
        "cursor-pointer rounded-lg bg-canvas p-5 ds-body transition-[border] duration-150",
        selected
          ? "border-2 border-selection" // radio-option-selected
          : "border border-ink-deep/12", // radio-option
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
