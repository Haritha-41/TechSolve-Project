import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SocialSense RAG",
  description: "Compare social media video transcripts with local RAG.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
