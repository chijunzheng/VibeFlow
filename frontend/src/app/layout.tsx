import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { ToastProvider } from "@/context/ToastContext";

export const metadata: Metadata = {
  title: "VibeFlow Studio",
  description: "AI Co-Writer for Songwriters",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 flex overflow-hidden">
        <ToastProvider>
            <Sidebar />
            <main className="flex-1 h-screen overflow-y-auto">
            {children}
            </main>
        </ToastProvider>
      </body>
    </html>
  );
}
