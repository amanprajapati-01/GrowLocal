"use client";

/** Selectable pill chip — audience pickers. Active state = button-pill-tab-active. */
export default function Chip({
  selected,
  onClick,
  children,
}: {
  selected?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selected}
      className={[
        "h-10 rounded-full px-4 ds-body-sm font-bold leading-none transition-colors",
        selected
          ? "bg-ink-deep text-white" // pill-tab-active
          : "border border-hairline bg-canvas text-ink",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
