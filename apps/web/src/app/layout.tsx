import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Job Coach",
  description: "A calm, evidence-based resume tailoring coach."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <ClerkProvider>
      <html lang="zh-CN">
        <body className={`${GeistSans.variable} ${GeistMono.variable}`}>{children}</body>
      </html>
    </ClerkProvider>
  );
}
