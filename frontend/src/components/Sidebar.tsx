"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Music, Home, Trash2, Library } from "lucide-react";
...
        <Link
          href="/"
          className={`flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors ${pathname === '/' ? 'bg-slate-800 text-white' : 'text-slate-300'}`}
        >
          <Home size={18} />
          Home
        </Link>

        <Link
          href="/library"
          className={`flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors ${pathname === '/library' ? 'bg-slate-800 text-white' : 'text-slate-300'}`}
        >
          <Library size={18} />
          Library
        </Link>
        
        <div className="mt-4 px-3 text-xs font-semibold text-slate-500 uppercase">
          Your Songs
        </div>
        
        <div className="mt-2 space-y-1">
          {songs.map((song) => (
            <Link
              key={song.id}
              href={`/songs/${song.id}`}
              className={`group flex items-center justify-between p-3 rounded-lg hover:bg-slate-800 transition-colors ${pathname === `/songs/${song.id}` ? 'bg-slate-800 text-white' : 'text-slate-300'}`}
            >
              <div className="flex items-center gap-3 truncate">
                <Music size={16} className="shrink-0" />
                <span className="truncate">{song.title}</span>
              </div>
              <button
                onClick={(e) => handleDelete(e, song.id)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-all"
              >
                <Trash2 size={14} />
              </button>
            </Link>
          ))}
          {songs.length === 0 && (
            <div className="p-3 text-xs text-slate-600 italic">No songs yet.</div>
          )}
        </div>
      </nav>
    </div>
  );
}