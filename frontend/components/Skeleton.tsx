/** Loading shimmer blocks (150–250ms ease per iteration guide). */
export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={`animate-pulse rounded-xl bg-surface-soft ${className}`}
    />
  );
}

const SkeletonDefault = Skeleton;
export default SkeletonDefault;

export function SkeletonCard() {
  return (
    <div className="glass-solid space-y-3 rounded-xl p-6">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-3 w-2/3" />
      <Skeleton className="h-3 w-1/2" />
    </div>
  );
}
