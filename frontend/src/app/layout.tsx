// Root layout — metadata and providers.

import type { Metadata } from "next";
import Providers from "../components/Providers";

export const metadata: Metadata = {
  title: "EconViz - Market Regime Dashboard",
  description:
    "Economic indicator dashboard using Hidden Markov Models for market regime detection and Monte Carlo simulations for price projections.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
