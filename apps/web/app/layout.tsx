import type { Metadata } from "next";
import { ReactNode } from "react";

import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Orcamento IA",
  description: "Preenchimento inteligente de planilhas de orçamento com IA."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

