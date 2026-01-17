"use client";

import { useEffect, useState, useRef } from "react";
import { fetchSong, generateVibe, writeLyrics, countSyllables, Song } from "@/lib/api";
import { Loader2, Sparkles, PenTool } from "lucide-react";

export default function SongEditor({ params }: { params: Promise<{ id: string }> }) {
  const [songId, setSongId] = useState<number | null>(null);
  
  useEffect(() => {
    params.then(p => setSongId(parseInt(p.id)));
  }, [params]);

  const [song, setSong] = useState<Song | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Vibe State
  const [vibePrompt, setVibePrompt] = useState("");
  const [generatingVibe, setGeneratingVibe] = useState(false);

  // Lyrics State
  const [lyrics, setLyrics] = useState("");
  const [syllableCounts, setSyllableCounts] = useState<number[]>([]);
  const [writingLyrics, setWritingLyrics] = useState(false);
  
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (songId) loadSong(songId);
  }, [songId]);

  useEffect(() => {
    if (lyrics) {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
      debounceTimer.current = setTimeout(() => {
        updateSyllableCounts(lyrics);
      }, 500);
    } else {
      setSyllableCounts([]);
    }
  }, [lyrics]);

  const loadSong = async (id: number) => {
    try {
      const data = await fetchSong(id);
      setSong(data);
      if (data.content?.lyrics) {
        setLyrics(data.content.lyrics);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateSyllableCounts = async (text: string) => {
    try {
      const counts = await countSyllables(text);
      setSyllableCounts(counts);
    } catch (err) {
      console.error("Syllable counting failed", err);
    }
  };

  const handleGenerateVibe = async () => {
    if (!song || !vibePrompt) return;
    setGeneratingVibe(true);
    try {
      const updatedSong = await generateVibe(song.id, vibePrompt);
      setSong(updatedSong);
    } catch (err) {
      alert("Failed to generate vibe");
    } finally {
      setGeneratingVibe(false);
    }
  };

  const handleWriteLyrics = async () => {
    if (!song) return;
    setWritingLyrics(true);
    try {
      const updatedSong = await writeLyrics(song.id);
      setSong(updatedSong);
      if (updatedSong.content?.lyrics) {
        setLyrics(updatedSong.content.lyrics);
      }
    } catch (err) {
      alert("Failed to write lyrics");
    } finally {
      setWritingLyrics(false);
    }
  };

  if (loading) return <div className="p-8 flex items-center justify-center"><Loader2 className="animate-spin" /></div>;
  if (!song) return <div className="p-8">Song not found</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <header className="mb-6 border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-bold text-white">{song.title}</h1>
        <p className="text-slate-500 text-sm">Created {new Date(song.created_at).toLocaleDateString()}</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left Panel: Vibe Engine */}
        <div className="lg:col-span-1 bg-slate-900/50 rounded-xl border border-slate-800 p-4 flex flex-col gap-4 overflow-y-auto">
          <div className="flex items-center gap-2 text-violet-400 font-semibold">
            <Sparkles size={18} />
            <h2>Vibe Cloud</h2>
          </div>
          
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Enter a vibe (e.g., Rain)"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-violet-500"
              value={vibePrompt}
              onChange={(e) => setVibePrompt(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleGenerateVibe()}
            />
            <button
              onClick={handleGenerateVibe}
              disabled={generatingVibe || !vibePrompt}
              className="w-full bg-violet-600/20 hover:bg-violet-600/40 text-violet-300 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {generatingVibe ? "Thinking..." : "Generate Vibe"}
            </button>
          </div>

          <div className="flex flex-wrap gap-2 mt-2">
            {song.vibe_cloud?.map((anchor, i) => (
              <span key={i} className="px-3 py-1 bg-slate-800/80 border border-slate-700 rounded-full text-xs text-slate-300">
                {anchor}
              </span>
            ))}
            {!song.vibe_cloud?.length && (
              <p className="text-slate-600 text-xs italic">No vibes generated yet.</p>
            )}
          </div>
        </div>

        {/* Center/Right Panel: Editor */}
        <div className="lg:col-span-2 bg-slate-900/50 rounded-xl border border-slate-800 p-4 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-200 font-semibold">
              <PenTool size={18} />
              <h2>Lyrics</h2>
            </div>
            <button
              onClick={handleWriteLyrics}
              disabled={writingLyrics || !song.vibe_cloud?.length}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {writingLyrics ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
              Ghostwrite
            </button>
          </div>

          <div className="flex-1 relative flex">
             <div className="w-10 bg-slate-950/30 border-r border-slate-800 flex flex-col pt-4 items-center text-[10px] text-slate-500 font-mono space-y-[1.15rem] pointer-events-none select-none">
                {syllableCounts.map((count, i) => (
                  <div key={i} className="h-4 flex items-center justify-center">
                    {count > 0 ? count : ""}
                  </div>
                ))}
             </div>
             <textarea
                className="flex-1 bg-slate-950/50 border-none rounded-r-lg p-4 text-slate-300 font-mono text-sm focus:outline-none resize-none leading-relaxed"
                placeholder="Start writing..."
                value={lyrics}
                onChange={(e) => setLyrics(e.target.value)}
              />
          </div>
        </div>
      </div>
    </div>
  );
}