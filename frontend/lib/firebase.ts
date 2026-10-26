/**
 * Firebase Auth (optional). Guest mode works with zero configuration:
 * if NEXT_PUBLIC_FIREBASE_* vars are missing, all helpers no-op gracefully.
 * Token plumbing is wired into lib/api via registerTokenProvider.
 */

"use client";

import { registerTokenProvider } from "@/lib/api";

type FirebaseUser = { uid: string; email: string | null; displayName: string | null };

export const firebaseEnabled = Boolean(
  process.env.NEXT_PUBLIC_FIREBASE_API_KEY && process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
);

let initialized = false;
let currentUser: FirebaseUser | null = null;
let tokenProviderReady = false;
const listeners = new Set<(u: FirebaseUser | null) => void>();

/** Lazily dynamic-import firebase so bundles stay lean and missing env vars never crash. */
async function ensureFirebase() {
  if (initialized || !firebaseEnabled) return;
  initialized = true;
  try {
    const [{ initializeApp, getApps }, authMod] = await Promise.all([
      import("firebase/app"),
      import("firebase/auth"),
    ]);
    if (getApps().length === 0) {
      initializeApp({
        apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
        authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
        projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
        storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
        messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
        appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
      });
    }
    const auth = authMod.getAuth();
    authMod.onAuthStateChanged(auth, (u) => {
      currentUser = u
        ? { uid: u.uid, email: u.email, displayName: u.displayName }
        : null;
      listeners.forEach((fn) => fn(currentUser));
      if (!tokenProviderReady) {
        tokenProviderReady = true;
        registerTokenProvider(async () => {
          if (!auth.currentUser) return null;
          return authMod.getIdToken(auth.currentUser);
        });
      }
    });
  } catch {
    /* Firebase misconfigured/unavailable → stay in guest mode quietly. */
  }
}

export function initAuth() {
  ensureFirebase();
}

export function getUser() {
  return currentUser;
}

export function onUserChange(fn: (u: FirebaseUser | null) => void) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export async function signInWithGoogle(): Promise<FirebaseUser | null> {
  if (!firebaseEnabled) return null;
  await ensureFirebase();
  const { getAuth, GoogleAuthProvider, signInWithPopup } = await import("firebase/auth");
  const auth = getAuth();
  const cred = await signInWithPopup(auth, new GoogleAuthProvider());
  return { uid: cred.user.uid, email: cred.user.email, displayName: cred.user.displayName };
}

/** Local-only guest session marker (uid lives in the backend under AUTH_DISABLED). */
const GUEST_KEY = "guest-session";

export function startGuestSession() {
  try {
    localStorage.setItem(GUEST_KEY, JSON.stringify({ startedAt: Date.now() }));
  } catch {
    /* storage unavailable */
  }
}

export function isGuest() {
  try {
    return Boolean(localStorage.getItem(GUEST_KEY));
  } catch {
    return false;
  }
}
