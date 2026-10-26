"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useState } from "react";
import TopBar from "@/components/TopBar";
import Card from "@/components/Card";
import { Button } from "@/components/Button";
import { firebaseEnabled, signInWithGoogle, startGuestSession } from "@/lib/firebase";

export default function LoginPage() {
  const t = useTranslations("login");
  const tE = useTranslations("errors");
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function guest() {
    startGuestSession();
    router.push("/start");
  }

  async function google() {
    setBusy(true);
    setError(null);
    try {
      if (!firebaseEnabled) {
        setError("generic");
        return;
      }
      await signInWithGoogle();
      router.push("/plans");
    } catch {
      setError("generic");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />
      <main className="mx-auto w-full max-w-md flex-1 px-5 pb-24">
        <h1 className="mt-8 ds-heading text-ink-deep">{t("title")}</h1>
        <p className="mt-2 text-charcoal ds-body">{t("sub")}</p>

        <Card className="mt-8 flex flex-col gap-4">
          <Button variant="primary" onClick={() => void google()} disabled={busy}>
            {busy ? t("working") : t("google")}
          </Button>

          <div className="flex items-center gap-3">
            <span className="h-px flex-1 bg-hairline-soft" />
            <span className="ds-caption-bold text-steel">{t("or")}</span>
            <span className="h-px flex-1 bg-hairline-soft" />
          </div>

          <Button variant="secondary" onClick={() => void guest()}>
            {t("guest")}
          </Button>

          <p className="text-center text-steel ds-caption">{t("guestNote")}</p>
        </Card>

        {error ? (
          <p className="mt-4 rounded-lg border border-critical-strong bg-canvas p-3 text-critical-strong ds-body-sm">
            {tE(error)}
          </p>
        ) : null}
      </main>
    </div>
  );
}
