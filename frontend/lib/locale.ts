/**
 * Locale type + helpers. No locale-prefixed routes: the locale lives in a
 * `locale` cookie (en|hi), read server-side by next-intl's request config.
 */

export const LOCALES = ["en", "hi"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "en";
export const LOCALE_COOKIE = "locale";

export function isLocale(v: string | undefined | null): v is Locale {
  return v === "en" || v === "hi";
}

/** Client-side helper for the language toggle: set cookie then reload. */
export function setLocaleCookie(locale: Locale) {
  document.cookie = `${LOCALE_COOKIE}=${locale}; path=/; max-age=31536000; samesite=lax`;
  window.location.reload();
}

export function readLocaleCookie(): Locale {
  const m = document.cookie.match(/(?:^|;\s*)locale=(en|hi)/);
  return m?.[1] === "hi" ? "hi" : "en";
}
