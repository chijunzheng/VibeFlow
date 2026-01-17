"use client";

import { Sparkles } from "lucide-react";

export default function ThinkingIndicator({ active }: { active: boolean }) {
  if (!active) return null;

  return (
    <div className="flex items-center gap-2 text-violet-400">
      <div className="relative">
        <Sparkles size={16} className="animate-pulse relative z-10" />
        <div className="absolute inset-0 bg-violet-500 rounded-full blur-md opacity-40 animate-ping" />
      </div>
      <span className="text-[10px] font-semibold uppercase tracking-wider animate-pulse">
        Gemini is thinking...
      </span>
    </div>
  );
}
