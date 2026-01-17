"use client";

import { useEffect, useState } from "react";
import { fetchSongs, deleteSong, Song } from "@/lib/api";
import Link from "next/link";
import { Music, Trash2, ExternalLink, Calendar, Clock } from "lucide-react";
import { useToast } from "@/context/ToastContext";

export default function Library() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadSongs();
  }, []);

  const loadSongs = async () => {
    try {
      const data = await fetchSongs();
      setSongs(data);
    } catch (err) {
      toast("Failed to load library", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this song?")) return;
    try {
      await deleteSong(id);
      setSongs(songs.filter(s => s.id !== id));
      toast("Song deleted", "success");
    } catch (err) {
      toast("Delete failed", "error");
    }
  };

  if (loading) return <div className="p-8 flex justify-center"><Clock className="animate-spin text-violet-500" /></div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Library</h1>
          <p className="text-slate-400 text-lg">Manage your songwriting projects.</p>
        </div>
      </header>

      {songs.length === 0 ? (
        <div className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-800 p-12 text-center shadow-xl">
          <Music size={48} className="mx-auto text-slate-700 mb-4" />
          <h2 className="text-xl font-semibold text-slate-300 mb-2">No songs found</h2>
          <p className="text-slate-500 mb-6">Start your first project from the sidebar.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {songs.map((song) => (
            <div 
              key={song.id}
              className="bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-800 p-6 flex flex-col gap-4 hover:border-violet-500/50 transition-all group shadow-xl"
            >
              <div className="flex justify-between items-start">
                <div className="w-10 h-10 bg-violet-600/20 rounded-xl flex items-center justify-center text-violet-400">
                  <Music size={20} />
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleDelete(song.id)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all"
                  >
                    <Trash2 size={16} />
                  </button>
                  <Link 
                    href={`/songs/${song.id}`}
                    className="p-2 text-slate-500 hover:text-violet-400 hover:bg-violet-400/10 rounded-lg transition-all"
                  >
                    <ExternalLink size={16} />
                  </Link>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-bold text-white group-hover:text-violet-300 transition-colors truncate">
                  {song.title}
                </h2>
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-slate-500">
                  <div className="flex items-center gap-1">
                    <Calendar size={12} />
                    {new Date(song.created_at).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock size={12} />
                    {new Date(song.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>

              <div className="mt-auto pt-4 border-t border-slate-800/50 flex flex-wrap gap-1">
                {song.vibe_cloud?.slice(0, 3).map((vibe, i) => (
                  <span key={i} className="px-2 py-0.5 bg-slate-800/50 rounded-full text-[10px] text-slate-400">
                    {vibe}
                  </span>
                ))}
                {(song.vibe_cloud?.length ?? 0) > 3 && (
                  <span className="text-[10px] text-slate-600 self-center">+{song.vibe_cloud!.length - 3} more</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
