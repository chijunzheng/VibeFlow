"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Music, Home } from "lucide-react";
import { fetchSongs, createSong, Song } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function Sidebar() {
  const [songs, setSongs] = useState<Song[]>([]);
  const router = useRouter();

  useEffect(() => {
    loadSongs();
  }, []);

  const loadSongs = async () => {
    try {
      const data = await fetchSongs();
      setSongs(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewSong = async () => {
    const title = prompt("Enter song title:");
    if (!title) return;
    try {
      const newSong = await createSong(title);
      setSongs([...songs, newSong]);
      router.push(`/songs/${newSong.id}`);
    } catch (err) {
      alert("Failed to create song");
    }
  };

  return (
    <div className="w-64 h-screen bg-slate-900 text-white flex flex-col border-r border-slate-800">
      <div className="p-4 border-b border-slate-800 flex items-center gap-2">
        <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
          <Music size={18} />
        </div>
        <h1 className="font-bold text-lg">VibeFlow</h1>
      </div>

      <div className="p-4">
        <button
          onClick={handleNewSong}
          className="w-full bg-violet-600 hover:bg-violet-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <Plus size={18} />
          New Song
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2">
        <Link
          href="/"
          className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
        >
          <Home size={18} />
          Home
        </Link>
        
        <div className="mt-4 px-3 text-xs font-semibold text-slate-500 uppercase">
          Your Songs
        </div>
        
        <div className="mt-2 space-y-1">
          {songs.map((song) => (
            <Link
              key={song.id}
              href={`/songs/${song.id}`}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors truncate"
            >
              <Music size={16} className="shrink-0" />
              <span className="truncate">{song.title}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}
