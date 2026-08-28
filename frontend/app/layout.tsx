import type { Metadata, Viewport } from "next";
import { Navigation } from "@/components/navigation/Navigation";
import { Providers } from "@/components/Providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Clinical Evidence Assistant",
  description:
    "Search scientific literature, compare evidence, verify citations, and explore uncertainty with an AI-assisted research workflow.",
  openGraph: {
    title: "Clinical Evidence Assistant",
    description: "Evidence-grounded biomedical research AI",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#006fc7",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <Navigation />
          <main className="lg:pl-64 min-h-screen pb-20 lg:pb-0">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
