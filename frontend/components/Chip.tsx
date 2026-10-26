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
        "h-10 rounded-full px-4 ds-body-sm font-bold leading-none transition-colors backdrop-blur-md",
        selected
          ? "glass-active"
          : "border border-white/16 bg-white/6 text-ink hover:bg-white/12",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
