"use client";

import Link from "next/link";
import { Music, Home } from "lucide-react";

export default function NotFound() {
  return (
    <div className="h-screen w-full flex items-center justify-center p-8 bg-slate-950">
      <div className="max-w-md w-full bg-slate-900/40 backdrop-blur-xl border border-slate-800 rounded-3xl p-12 text-center shadow-2xl animate-in zoom-in duration-300">
        <div className="w-16 h-16 bg-violet-600/20 rounded-2xl flex items-center justify-center text-violet-400 mx-auto mb-6 shadow-[0_0_20px_rgba(139,92,246,0.2)]">
          <Music size={32} />
        </div>
        <h1 className="text-6xl font-black text-white mb-4 tracking-tighter">404</h1>
        <h2 className="text-xl font-bold text-slate-200 mb-4">Song Not Found</h2>
        <p className="text-slate-500 mb-8 leading-relaxed">
          The project you're looking for has drifted off into the void. 
          Maybe it's time to start a new melody?
        </p>
        <Link 
          href="/"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 shadow-lg shadow-violet-600/20"
        >
          <Home size={18} />
          Go Home
        </Link>
      </div>
    </div>
  );
}
