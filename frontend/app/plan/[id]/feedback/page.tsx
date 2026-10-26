import TopBar from "@/components/TopBar";
import FeedbackForm from "@/components/FeedbackForm";

/** S8 feedback page. */
export default async function FeedbackPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />
      <main className="flex-1">
        <FeedbackForm planId={id} />
      </main>
    </div>
  );
}
