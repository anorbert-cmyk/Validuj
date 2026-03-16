import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://validuj.example"),
  title: {
    default: "Validuj — production-ready startup validation platform",
    template: "%s | Validuj",
  },
  description:
    "Validate startup ideas with a production-ready six-agent workflow covering market research, competitors, strategy, product design, edge cases, and risk analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} bg-slate-950 text-slate-50 antialiased`}
      >
        <Providers>
          <div className="min-h-screen bg-[radial-gradient(circle_at_top,#172554_0%,#020617_55%)]">
            <header className="border-b border-white/10 backdrop-blur-sm">
              <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
                <Link href="/" className="text-lg font-semibold tracking-tight text-white">
                  Validuj
                </Link>
                <nav className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
                  <Link href="/how-it-works" className="transition hover:text-white">
                    How it works
                  </Link>
                  <Link href="/pricing" className="transition hover:text-white">
                    Pricing
                  </Link>
                  <Link href="/compare" className="transition hover:text-white">
                    Compare
                  </Link>
                  <Link href="/demo-report" className="transition hover:text-white">
                    Demo report
                  </Link>
                  <Link href="/security" className="transition hover:text-white">
                    Security
                  </Link>
                  <Link
                    href="/dashboard"
                    className="rounded-full border border-cyan-400/30 px-4 py-2 text-cyan-200 transition hover:border-cyan-300 hover:text-white"
                  >
                    Dashboard
                  </Link>
                  <Link href="/settings" className="transition hover:text-white">
                    Settings
                  </Link>
                  <Link href="/admin" className="transition hover:text-white">
                    Admin
                  </Link>
                </nav>
              </div>
            </header>
            <main>{children}</main>
            <footer className="border-t border-white/10 bg-slate-950/60">
              <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-6 py-10 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-medium text-slate-200">Validuj</p>
                  <p>Production-ready startup validation with a six-agent handoff workflow.</p>
                </div>
                <div className="flex flex-wrap gap-4">
                  <Link href="/faq" className="transition hover:text-white">
                    FAQ
                  </Link>
                  <Link href="/pricing" className="transition hover:text-white">
                    Pricing
                  </Link>
                  <Link href="/how-it-works" className="transition hover:text-white">
                    Methodology
                  </Link>
                </div>
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
