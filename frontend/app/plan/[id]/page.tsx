import TopBar from "@/components/TopBar";
import PlanDashboard from "@/components/PlanDashboard";

/** S5 plan dashboard. params is a Promise in Next 16. */
export default async function PlanPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />
      <main className="flex-1">
        <PlanDashboard planId={id} />
      </main>
    </div>
  );
}
