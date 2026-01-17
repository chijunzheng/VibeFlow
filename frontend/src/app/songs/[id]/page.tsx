"use client";

import { useEffect, useState, use } from "react";
import { fetchSong, generateVibe, writeLyrics, Song } from "@/lib/api";
import { Loader2, Sparkles, PenTool } from "lucide-react";

export default function SongEditor({ params }: { params: Promise<{ id: string }> }) {
  // Use React.use() to unwrap params in Next.js 15+ (Next.js 14 also supports async params in server components, but this is client)
  // Actually params is a promise in recent Next.js versions for client components too often?
  // Let's assume standard client component behavior where params is passed. 
  // Wait, in Next 15 params is a Promise. In Next 14 it's an object. 
  // The scaffold used "create-next-app@latest" which is likely Next 15 or 14. 
  // I will use `use(params)` pattern if it's a promise, or just wait for it.
  
  // Safe approach for Next 14/15 compat:
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
  const [writingLyrics, setWritingLyrics] = useState(false);

  useEffect(() => {
    if (songId) loadSong(songId);
  }, [songId]);

  const loadSong = async (id: number) => {
    try {
      const data = await fetchSong(id);
      setSong(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
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

          <textarea
            className="flex-1 w-full bg-slate-950/50 border border-slate-800 rounded-lg p-4 text-slate-300 font-mono text-sm focus:outline-none focus:border-slate-700 resize-none leading-relaxed"
            placeholder="Lyrics will appear here..."
            value={song.content?.lyrics || ""}
            readOnly // For now, read only until manual edit feature
          />
        </div>
      </div>
    </div>
  );
}
