"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import TopBar from "@/components/TopBar";
import ErrorState from "@/components/ErrorState";
import { postPlan, ApiError, type PlanInput } from "@/lib/api";

const STAGES = ["stage1", "stage2", "stage3", "stage4", "stage5"] as const;
/** Stage i is "done" after this many ms; generation may finish faster. */
const STAGE_MS = [800, 1800, 3200, 4800, 6200];

const STORAGE_KEY = "growlocal.planRequest";

export default function GeneratingPage() {
  const tG = useTranslations("generating");
  const router = useRouter();
  const [stage, setStage] = useState(1); // 1..5; 0 = failed
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  const clearTimers = () => {
    timers.current.forEach((t) => clearTimeout(t));
    timers.current = [];
  };

  /** No direct setState in the effect call chain: states change only in timer/promise callbacks. */
  const generate = useCallback(() => {
    let input: PlanInput;
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) {
        router.push("/start");
        return;
      }
      input = JSON.parse(raw) as PlanInput;
    } catch {
      router.push("/start");
      return;
    }

    // Advance the visual stages while the request is pending.
    STAGE_MS.forEach((ms, i) => {
      timers.current.push(
        setTimeout(() => setStage(Math.min(i + 2, 5)), ms)
      );
    });

    const started = Date.now();
    return postPlan(input)
      .then((res) => {
        // Ensure the last stages are seen (demo pacing) before redirect.
        const wait = Math.max(0, 5200 - (Date.now() - started));
        timers.current.push(
          setTimeout(() => {
            timers.current.push(
              setTimeout(() => router.push(`/plan/${encodeURIComponent(res.planId)}`), 700)
            );
          }, wait)
        );
      })
      .catch((e: unknown) => {
        clearTimers();
        const code = e instanceof ApiError ? e.code : "generic";
        setErrorCode(code === "rate_limited" ? "rateLimited" : "generic");
        setStage(0);
      });
  }, [router]);

  function retry() {
    clearTimers();
    setStage(1);
    setErrorCode(null);
    void generate();
  }

  useEffect(() => {
    void generate();
    return clearTimers;
  }, [generate]);

  if (stage === 0) {
    return (
      <div className="flex min-h-dvh flex-col">
        <TopBar />
        <main className="mx-auto w-full max-w-md flex-1 px-5 py-16 text-center">
          <ErrorState code={errorCode} onRetry={retry} />
          <Link
            href="/start"
            className="mt-6 inline-block ds-body-sm font-bold text-steel underline"
          >
            {tG("failedTitle")}
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />
      <main className="mx-auto w-full max-w-md flex-1 px-5 py-14">
        <h1 className="ds-heading text-ink-deep">{tG("title")}</h1>
        <p className="mt-2 text-charcoal ds-body-sm">{tG("sub")}</p>

        <ol className="glass mt-10 flex flex-col gap-4 rounded-xl p-6">
          {STAGES.map((s, i) => {
            const n = i + 1;
            const done = stage > n;
            const active = !done && stage === n;
            return (
              <li key={s} className="flex items-center gap-3">
                <span
                  aria-hidden
                  className={[
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 ds-caption-bold",
                    done
                      ? "border-success bg-success text-white"
                      : active
                        ? "border-white/40 bg-white/10 text-white shadow-[0_0_16px_rgba(77,155,255,0.35)]"
                        : "border-white/12 text-stone",
                  ].join(" ")}
                >
                  {done ? "✓" : n}
                </span>
                <span
                  className={[
                    "ds-body",
                    done ? "text-charcoal" : active ? "font-bold text-white" : "text-stone",
                  ].join(" ")}
                >
                  {tG(s)}
                </span>
              </li>
            );
          })}
        </ol>
      </main>
    </div>
  );
}
