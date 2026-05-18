import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Opportunity Radar",
  description: "A personalized AI-powered intelligence dashboard.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

