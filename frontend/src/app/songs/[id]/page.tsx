"use client";

import { useEffect, useState, useRef } from "react";
import { fetchSong, generateVibe, getStreamLyricsUrl, countSyllables, analyzeStress, updateSong, Song } from "@/lib/api";
import { Loader2, Sparkles, PenTool, Activity, Edit2, Check, X, Copy, CheckCircle2 } from "lucide-react";

export default function SongEditor({ params }: { params: Promise<{ id: string }> }) {
  const [songId, setSongId] = useState<number | null>(null);
  
  useEffect(() => {
    params.then(p => setSongId(parseInt(p.id)));
  }, [params]);

  const [song, setSong] = useState<Song | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Title State
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState("");

  // Vibe State
  const [vibePrompt, setVibePrompt] = useState("");
  const [generatingVibe, setGeneratingVibe] = useState(false);

  // Lyrics State
  const [lyrics, setLyrics] = useState("");
  const [syllableCounts, setSyllableCounts] = useState<number[]>([]);
  const [writingLyrics, setWritingLyrics] = useState(false);
  const [rhymeScheme, setRhymeScheme] = useState("Free Verse");
  
  // Stress State
  const [showStress, setShowStress] = useState(false);
  const [stressContent, setStressContent] = useState("");
  const [analyzingStress, setAnalyzingStress] = useState(false);
  
  // Auto-save State
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Export State
  const [copied, setCopied] = useState(false);
  
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const saveTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (songId) loadSong(songId);
  }, [songId]);

  useEffect(() => {
    if (lyrics) {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
      debounceTimer.current = setTimeout(() => {
        updateSyllableCounts(lyrics);
      }, 500);
      
      if (song && !loading && !writingLyrics) {
        if (saveTimer.current) clearTimeout(saveTimer.current);
        setSaving(true);
        saveTimer.current = setTimeout(() => {
            handleAutoSave(lyrics);
        }, 2000);
      }
    } else {
      setSyllableCounts([]);
    }
  }, [lyrics]);
  
  const handleAutoSave = async (text: string) => {
    if (!song) return;
    try {
        await updateSong(song.id, { 
            content: { ...song.content, lyrics: text } 
        });
        setLastSaved(new Date());
    } catch (err) {
        console.error("Auto-save failed", err);
    } finally {
        setSaving(false);
    }
  };

  const loadSong = async (id: number) => {
    try {
      const data = await fetchSong(id);
      setSong(data);
      setTitleInput(data.title);
      if (data.content?.lyrics) {
        setLyrics(data.content.lyrics);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRename = async () => {
    if (!song || !titleInput.trim()) return;
    try {
        const updated = await updateSong(song.id, { title: titleInput });
        setSong(updated);
        setIsEditingTitle(false);
    } catch (err) {
        alert("Rename failed");
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
    setLyrics("");
    setShowStress(false);
    
    try {
      const url = getStreamLyricsUrl(song.id, "Modern", rhymeScheme);
      const response = await fetch(url);
      
      if (!response.body) throw new Error("No response body");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let finished = false;
      let accumulatedLyrics = "";

      while (!finished) {
        const { value, done } = await reader.read();
        finished = done;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          accumulatedLyrics += chunk;
          setLyrics(accumulatedLyrics);
        }
      }
      
      loadSong(song.id);
      
    } catch (err) {
      console.error(err);
      alert("Failed to stream lyrics");
    } finally {
      setWritingLyrics(false);
    }
  };
  
  const handleToggleStress = async () => {
    if (showStress) {
      setShowStress(false);
      return;
    }
    if (!lyrics) return;
    setAnalyzingStress(true);
    try {
      const stressText = await analyzeStress(lyrics);
      setStressContent(stressText);
      setShowStress(true);
    } catch (err) {
      alert("Failed to analyze stress");
    } finally {
      setAnalyzingStress(false);
    }
  };

  const handleCopy = async () => {
    if (!lyrics) return;
    try {
      await navigator.clipboard.writeText(lyrics);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };
  
  const renderStressContent = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i} className="text-violet-300 font-bold">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  if (loading) return <div className="p-8 flex items-center justify-center"><Loader2 className="animate-spin" /></div>;
  if (!song) return <div className="p-8">Song not found</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <header className="mb-6 border-b border-slate-800 pb-4 flex justify-between items-end">
        <div className="flex-1">
            {isEditingTitle ? (
                <div className="flex items-center gap-2">
                    <input
                        autoFocus
                        className="text-3xl font-bold bg-slate-900 border border-violet-500 rounded px-2 py-1 outline-none text-white w-full max-w-md"
                        value={titleInput}
                        onChange={(e) => setTitleInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") handleRename();
                            if (e.key === "Escape") setIsEditingTitle(false);
                        }}
                    />
                    <button onClick={handleRename} className="p-2 text-green-400 hover:bg-slate-800 rounded"><Check size={20}/></button>
                    <button onClick={() => setIsEditingTitle(false)} className="p-2 text-slate-400 hover:bg-slate-800 rounded"><X size={20}/></button>
                </div>
            ) : (
                <div className="group flex items-center gap-3">
                    <h1 className="text-3xl font-bold text-white">{song.title}</h1>
                    <button 
                        onClick={() => setIsEditingTitle(true)}
                        className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-violet-400 transition-all"
                    >
                        <Edit2 size={16} />
                    </button>
                </div>
            )}
            <p className="text-slate-500 text-sm mt-1">Created {new Date(song.created_at).toLocaleDateString()}</p>
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-2 pb-1">
            {saving ? (
                <span className="flex items-center gap-1 text-violet-400">
                    <Loader2 size={10} className="animate-spin" /> Saving...
                </span>
            ) : lastSaved ? (
                <span className="text-slate-400">Saved {lastSaved.toLocaleTimeString()}</span>
            ) : null}
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left Panel: Vibe Engine */}
        <div className="lg:col-span-1 bg-slate-900/40 backdrop-blur-md rounded-xl border border-slate-800/50 p-4 flex flex-col gap-4 overflow-y-auto shadow-xl">
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
              <span key={i} className="px-3 py-1 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-full text-xs text-slate-300">
                {anchor}
              </span>
            ))}
            {!song.vibe_cloud?.length && (
              <p className="text-slate-600 text-xs italic">No vibes generated yet.</p>
            )}
          </div>
        </div>

        {/* Center/Right Panel: Editor */}
        <div className="lg:col-span-2 bg-slate-900/40 backdrop-blur-md rounded-xl border border-slate-800/50 p-4 flex flex-col gap-4 overflow-hidden shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-200 font-semibold">
              <PenTool size={18} />
              <h2>Lyrics</h2>
            </div>
            <div className="flex gap-2">
                <button
                  onClick={handleCopy}
                  disabled={!lyrics}
                  className="bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 px-3 py-1.5 rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center gap-2 border border-slate-700/30"
                  title="Copy to clipboard"
                >
                  {copied ? <CheckCircle2 size={12} className="text-green-400" /> : <Copy size={12} />}
                  {copied ? "Copied" : "Copy"}
                </button>
                <select 
                    value={rhymeScheme}
                    onChange={(e) => setRhymeScheme(e.target.value)}
                    disabled={writingLyrics}
                    className="bg-slate-800 text-slate-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-violet-500 border border-slate-700/30"
                >
                    <option value="Free Verse">Free Verse</option>
                    <option value="AABB">AABB</option>
                    <option value="ABAB">ABAB</option>
                    <option value="ABBA">ABBA</option>
                </select>
                <button
                  onClick={handleToggleStress}
                  disabled={analyzingStress || !lyrics}
                  className={`px-3 py-1.5 rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center gap-2 border border-slate-700/30 ${
                    showStress 
                      ? "bg-violet-600 text-white" 
                      : "bg-slate-800/50 hover:bg-slate-700/50 text-slate-300"
                  }`}
                >
                  {analyzingStress ? <Loader2 size={12} className="animate-spin" /> : <Activity size={12} />}
                  Stress
                </button>
                <button
                  onClick={handleWriteLyrics}
                  disabled={writingLyrics || !song.vibe_cloud?.length}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center gap-2 border border-slate-700/30"
                >
                  {writingLyrics ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                  Ghostwrite
                </button>
            </div>
          </div>
          <div className="flex-1 relative flex overflow-hidden rounded-lg border border-slate-800/50">
             <div className="w-10 bg-slate-950/40 backdrop-blur-sm border-r border-slate-800/50 flex flex-col pt-4 items-center text-[10px] text-slate-500 font-mono space-y-[1.15rem] pointer-events-none select-none overflow-hidden">
                {syllableCounts.map((count, i) => (
                  <div key={i} className="h-4 flex items-center justify-center">
                    {count > 0 ? count : ""}
                  </div>
                ))}
             </div>
             {showStress ? (
                 <div className="flex-1 bg-slate-950/20 p-4 text-slate-300 font-mono text-sm overflow-y-auto leading-relaxed whitespace-pre-wrap">
                    {renderStressContent(stressContent)}
                 </div>
             ) : (
                 <textarea
                    className="flex-1 bg-slate-950/20 p-4 text-slate-300 font-mono text-sm focus:outline-none resize-none leading-relaxed"
                    placeholder="Start writing..."
                    value={lyrics}
                    onChange={(e) => setLyrics(e.target.value)}
                  />
             )}
          </div>
        </div>
      </div>
    </div>
  );
}