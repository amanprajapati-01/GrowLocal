/**
 * Typed API client for the GrowLocal FastAPI backend.
 * - Base URL from NEXT_PUBLIC_API_BASE_URL (default http://localhost:8000).
 * - Attaches Firebase ID token when a token provider is registered (guest mode: none).
 * - Normalizes errors to ApiError; backend returns {"error": {"code", "message"}}.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

if (process.env.NODE_ENV === "production" && API_BASE_URL.includes("localhost")) {
  // Deployed build without NEXT_PUBLIC_API_BASE_URL → requests would hit the
  // visitor's own machine and fail. Shout it into the console for a fast fix.
  console.error(
    "[GrowLocal] NEXT_PUBLIC_API_BASE_URL is not set — API calls target " +
      API_BASE_URL +
      ". Set the env var in your hosting provider's project settings and redeploy."
  );
}

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code || "unknown";
  }
}

/** Firebase is optional; register a provider in lib/firebase so guest mode works with no config. */
let tokenProvider: (() => Promise<string | null>) | null = null;

export function registerTokenProvider(fn: () => Promise<string | null>) {
  tokenProvider = fn;
}

async function authHeaders(): Promise<Record<string, string>> {
  if (!tokenProvider) return {};
  try {
    const token = await tokenProvider();
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

async function request<T>(path: string, init?: RequestInit & { json?: unknown }): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(init?.json !== undefined ? { "Content-Type": "application/json" } : {}),
    ...(await authHeaders()),
  };

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
      body: init?.json !== undefined ? JSON.stringify(init.json) : init?.body,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(0, "network", "network");
  }

  if (!res.ok) {
    let code = "unknown";
    let message = `HTTP ${res.status}`;
    try {
      const data = (await res.json()) as { error?: { code?: string; message?: string } };
      if (data?.error?.code) code = data.error.code;
      if (data?.error?.message) message = data.error.message;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, code, message);
  }

  return (await res.json()) as T;
}

/* ================= Types (mirror backend app/models/) ================= */

export type Language = "en" | "hi";

export type PlanInput = {
  businessType: string; // bakery | salon | restaurant | kirana | clinic | coaching | retail | other
  businessName: string;
  city: string;
  locality: string;
  monthlyBudgetInr: number; // 0..100000
  goal: string; // more_walk_ins | online_orders | repeat_customers | brand_awareness
  targetAudience: string[]; // families | students | professionals | women | seniors | tourists
  targetAudienceText?: string;
  language: Language;
};

export type Persona = {
  name: string;
  summary: string;
  ageRange: string;
  whereTheySpendTime: string[];
  whatTheyRespondTo: string[];
  buyingTriggers: string[];
};

export type ChannelRecommendation = {
  channelId: string;
  score: number; // 0..100
  budgetInr: number;
  rationale: string;
  expectedResult: string; // honest estimate range
  howToStart: string[]; // 1..3 steps
};

export type BudgetItem = { channelId: string; amountInr: number };

export type StartFreeAction = { title: string; minutes: number; channelId: string };

export type Task = {
  /** Client-side positional id: t_w{week}_n{index-1} (0-based, matches backend). */
  id?: string;
  title: string;
  channelId: string;
  minutes: number;
  costInr: number;
  done: boolean;
};

export type Week = { week: number; theme: string; tasks: Task[] };

export type FestivalSuggestion = { name: string; date: string; suggestedOffer: string };

/** PlanResponse from the backend. Plan/persona text comes in the requested language only. */
export type PlanResponse = {
  planId: string;
  persona: Persona;
  channels: ChannelRecommendation[];
  budgetAllocation: { totalInr: number; bufferInr: number; items: BudgetItem[] };
  startFreeToday: StartFreeAction[];
  actionPlan: { weeks: Week[] };
  festivals: FestivalSuggestion[];
  disclaimer: string;
  createdAt: string;
  modelUsed: string;
  generationMs: number;
  status: string;
};

export type PlanSummary = {
  planId: string;
  businessName: string;
  businessType: string;
  city: string;
  locality: string;
  goal: string;
  language: Language;
  monthlyBudgetInr: number;
  allocatedInr: number;
  bufferInr: number;
  status: string;
  createdAt: string;
};

export type ChannelMeta = {
  id: string;
  name: { en: string; hi: string };
  costType: "free" | "paid";
  effort: string;
  timeToResult: string;
};

export type ContentPack = {
  planId: string;
  language: Language;
  whatsapp: Array<{ label: string; text: string }>;
  instagram: Array<{ caption: string; hashtags: string[]; reelIdea: string }>;
  gbpPost: { title: string; body: string; ctaType: string } | null;
  offers: Array<{ name: string; description: string; validityDays: number }>;
  createdAt: string;
  modelUsed: string;
};

export type FeedbackPayload = {
  planId: string;
  channelId: string;
  outcome: "worked" | "partial" | "didnt";
  note?: string;
};

export type Competitor = {
  name: string;
  rating: number;
  reviewCount: number;
  address: string;
};

/* ================= Endpoint helpers ================= */

/** Build the positional task id used by the backend: t_w{week}_n{0-based index}. */
export function taskId(week: number, zeroBasedIndex: number): string {
  return `t_w${week}_n${zeroBasedIndex}`;
}

export function postPlan(input: PlanInput, signal?: AbortSignal) {
  return request<PlanResponse>("/api/plan", { method: "POST", json: input, signal });
}

export function listPlans() {
  return request<{ plans: PlanSummary[] }>("/api/plans");
}

export function getPlan(planId: string, signal?: AbortSignal) {
  return request<PlanResponse>(`/api/plans/${encodeURIComponent(planId)}`, { signal });
}

export function patchTask(planId: string, id: string, done: boolean) {
  return request<Record<string, unknown>>(
    `/api/plans/${encodeURIComponent(planId)}/tasks/${encodeURIComponent(id)}`,
    { method: "PATCH", json: { done } }
  );
}

export function getChannels(signal?: AbortSignal) {
  return request<{ channels: ChannelMeta[] }>("/api/channels", { signal });
}

export function postContent(
  planId: string,
  language: Language,
  types: string[] = ["whatsapp", "instagram", "gbp_post", "offer"],
  signal?: AbortSignal
) {
  return request<ContentPack>("/api/content", {
    method: "POST",
    json: { planId, language, types },
    signal,
  });
}

export function getContent(planId: string, language: Language) {
  return request<{ pack: ContentPack | null }>(
    `/api/content/${encodeURIComponent(planId)}?language=${language}`
  );
}

export function postFeedback(payload: FeedbackPayload) {
  return request<{ feedbackId: string; status: string }>("/api/feedback", {
    method: "POST",
    json: payload,
  });
}

/** P1: nearby competitor snapshot (GET /api/places). Empty + note without a Places key. */
export function getCompetitors(
  lat: number,
  lng: number,
  type = "",
  radius = 2500,
  signal?: AbortSignal
) {
  const qs = new URLSearchParams({
    lat: String(lat),
    lng: String(lng),
    radius: String(radius),
  });
  if (type) qs.set("type", type);
  return request<{ competitors: Competitor[]; note: string; radiusMeters: number }>(
    `/api/places?${qs.toString()}`,
    { signal }
  );
}
