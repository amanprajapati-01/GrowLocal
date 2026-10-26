import type { Metadata, Viewport } from "next";
import { Inter, Noto_Sans_Devanagari } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";
import ToastProvider from "@/components/Toast";
import BottomNav from "@/components/BottomNav";
import "@/app/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const notoDev = Noto_Sans_Devanagari({
  subsets: ["devanagari", "latin"],
  weight: ["400", "700"],
  variable: "--font-noto-dev",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "GrowLocal — free marketing plans for local businesses",
    template: "%s · GrowLocal",
  },
  description:
    "Free-first, budget-aware marketing plans for Indian local businesses. In Hindi and English.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale} className={`${inter.variable} ${notoDev.variable}`}>
      <body className="pb-20 min-h-dvh bg-canvas text-ink antialiased sm:pb-0">
        <NextIntlClientProvider messages={messages}>
          <ToastProvider>
            {children}
            <BottomNav />
          </ToastProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
