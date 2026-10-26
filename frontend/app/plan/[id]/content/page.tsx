import TopBar from "@/components/TopBar";
import ContentStudio from "@/components/ContentStudio";
import { getLocale } from "next-intl/server";

/** S6 content studio. */
export default async function ContentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const locale = await getLocale();
  const language = locale === "hi" ? "hi" : "en";

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />
      <main className="flex-1">
        <ContentStudio planId={id} language={language} />
      </main>
    </div>
  );
}
