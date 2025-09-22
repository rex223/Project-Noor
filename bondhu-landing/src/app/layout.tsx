import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Bondhu - AI Mental Health Companion",
  description: "Meet your digital বন্ধু - an AI companion that adapts to your personality, grows with your journey, and becomes the friend you've always needed.",
  keywords: ["AI", "mental health", "companion", "chatbot", "wellness", "friendship", "Gen Z"],
  authors: [{ name: "Bondhu Team" }],
  openGraph: {
    title: "Bondhu - AI Mental Health Companion",
    description: "Meet your digital বন্ধু - an AI companion that adapts to your personality, grows with your journey, and becomes the friend you've always needed.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange={false}
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
