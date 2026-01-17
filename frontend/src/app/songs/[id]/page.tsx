"use client";

import { useEffect, useState, useRef } from "react";
import { fetchSong, generateVibe, getStreamLyricsUrl, countSyllables, analyzeStress, rewriteText, updateSong, Song } from "@/lib/api";
import { Loader2, Sparkles, PenTool, Activity, Edit2, Check, X, Copy, CheckCircle2, RotateCcw, Trash } from "lucide-react";
import { useToast } from "@/context/ToastContext";
import ThinkingIndicator from "@/components/ThinkingIndicator";

export default function SongEditor({ params }: { params: Promise<{ id: string }> }) {
  const { toast } = useToast();
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
  
  // Rewrite State
  const [rewriting, setRewriting] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const saveTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        handleWriteLyrics();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        if (lyrics) handleAutoSave(lyrics);
      }
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "S") {
        e.preventDefault();
        handleToggleStress();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [lyrics, song, writingLyrics, analyzingStress, rhymeScheme]); // Dependencies for state-accessing functions

  useEffect(() => {
    if (songId) loadSong(songId);
  }, [songId]);

  useEffect(() => {
    if (lyrics) {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
      debounceTimer.current = setTimeout(() => {
        updateSyllableCounts(lyrics);
      }, 500);
      
      if (song && !loading && !writingLyrics && !rewriting) {
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
      toast("Failed to load song", "error");
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
        toast("Song renamed", "success");
    } catch (err) {
        toast("Rename failed", "error");
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
      toast("Vibe Cloud generated", "success");
      setVibePrompt("");
    } catch (err) {
      toast("Failed to generate vibe", "error");
    } finally {
      setGeneratingVibe(false);
    }
  };

  const handleWriteLyrics = async () => {
    if (!song) return;
    setWritingLyrics(true);
    setLyrics("");
    setShowStress(false);
    const seedText = vibePrompt.trim();
    
    try {
      const url = getStreamLyricsUrl(
        song.id,
        "Modern",
        rhymeScheme,
        seedText ? seedText : undefined
      );
      const response = await fetch(url);
      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || `Request failed (${response.status})`);
      }
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
      toast("Lyrics drafted", "success");
      // Explicitly save the final result since auto-save effect might miss it due to writingLyrics lock
      await handleAutoSave(accumulatedLyrics); 
      const refreshed = await fetchSong(song.id);
      setSong(refreshed);
    } catch (err) {
      console.error(err);
      toast("Failed to draft lyrics", "error");
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
      toast("Stress patterns analyzed", "success");
    } catch (err) {
      toast("Analysis failed", "error");
    } finally {
      setAnalyzingStress(false);
    }
  };

  const handleCopy = async () => {
    if (!lyrics) return;
    try {
      await navigator.clipboard.writeText(lyrics);
      setCopied(true);
      toast("Copied to clipboard", "success");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast("Failed to copy", "error");
    }
  };

  const handleClearAll = async () => {
    if (!song || !confirm("Clear all vibes and lyrics?")) return;
    try {
        const updated = await updateSong(song.id, { 
            vibe_cloud: [], 
            content: { ...song.content, lyrics: "" },
            thought_sig: ""
        });
        setSong(updated);
        setLyrics("");
        toast("Session cleared", "success");
    } catch (err) {
        toast("Clear failed", "error");
    }
  };

  const handleRewrite = async () => {
    if (!song || !lyrics || !textareaRef.current) return;
    
    const selection = lyrics.substring(
        textareaRef.current.selectionStart,
        textareaRef.current.selectionEnd
    );

    if (!selection) {
        toast("Select some text to rewrite", "info");
        return;
    }

    const instructions = prompt("How should I rewrite this?", "Make it more poetic");
    if (!instructions) return;

    setRewriting(true);
    try {
        const result = await rewriteText(lyrics, selection, instructions);
        const newLyrics = lyrics.replace(selection, result);
        setLyrics(newLyrics);
        handleAutoSave(newLyrics); // Immediate save for rewrite
        toast("Text rewritten", "success");
    } catch (err) {
        toast("Rewrite failed", "error");
    } finally {
        setRewriting(false);
    }
  };

  const handleInsertVibe = (vibe: string) => {
    if (!textareaRef.current) return;
    
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    const newText = lyrics.substring(0, start) + vibe + lyrics.substring(end);
    setLyrics(newText);
    
    // Defer focus/selection update slightly to let React render
    setTimeout(() => {
        if (textareaRef.current) {
            textareaRef.current.focus();
            const newCursorPos = start + vibe.length;
            textareaRef.current.setSelectionRange(newCursorPos, newCursorPos);
        }
    }, 0);
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

  if (loading) return <div className="p-8 flex items-center justify-center h-screen"><Loader2 className="animate-spin text-violet-500" /></div>;
  if (!song) return <div className="p-8">Song not found</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <header className="mb-6 border-b border-slate-800 pb-4 flex justify-between items-end">
        <div className="flex-1">
            {isEditingTitle ? (
                <div className="flex items-center gap-2">
                    <input
                        autoFocus
                        className="text-3xl font-bold bg-slate-900 border border-violet-500 rounded px-2 py-1 outline-none text-white w-full max-w-md shadow-[0_0_15px_rgba(139,92,246,0.3)]"
                        value={titleInput}
                        onChange={(e) => setTitleInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") handleRename();
                            if (e.key === "Escape") setIsEditingTitle(false);
                        }}
                    />
                    <button onClick={handleRename} className="p-2 text-green-400 hover:bg-slate-800 rounded transition-colors"><Check size={20}/></button>
                    <button onClick={() => setIsEditingTitle(false)} className="p-2 text-slate-400 hover:bg-slate-800 rounded transition-colors"><X size={20}/></button>
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
            <p className="text-slate-500 text-sm mt-1 flex items-center gap-3">
                <span>Created {new Date(song.created_at).toLocaleDateString()}</span>
                {song.total_tokens > 0 && (
                    <span className="flex items-center gap-1 text-[10px] bg-slate-800/50 px-2 py-0.5 rounded-full border border-slate-700/50">
                        <Activity size={10} className="text-violet-400" />
                        {song.total_tokens.toLocaleString()} tokens
                    </span>
                )}
            </p>
        </div>
        <div className="flex flex-col items-end gap-2 pb-1">
            <ThinkingIndicator active={generatingVibe || writingLyrics || analyzingStress || rewriting} />
            <div className="text-[10px] text-slate-500">
                {saving ? (
                    <span className="flex items-center gap-1 text-violet-400">
                        <Loader2 size={10} className="animate-spin" /> Saving...
                    </span>
                ) : lastSaved ? (
                    <span className="text-slate-400">Saved {lastSaved.toLocaleTimeString()}</span>
                ) : null}
            </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left Panel: Vibe Engine */}
        <div className="lg:col-span-1 bg-slate-900/40 backdrop-blur-md rounded-xl border border-slate-800/50 p-4 flex flex-col gap-4 overflow-y-auto shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-violet-400 font-semibold">
                <Sparkles size={18} />
                <h2>Vibe Cloud</h2>
            </div>
            <button 
                onClick={handleClearAll}
                className="p-1.5 text-slate-600 hover:text-red-400 transition-colors"
                title="Clear all"
            >
                <Trash size={14} />
            </button>
          </div>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Seed phrase (e.g., Protective love)"
              className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-violet-500 transition-colors shadow-inner"
              value={vibePrompt}
              onChange={(e) => setVibePrompt(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleGenerateVibe()}
            />
            <button
              onClick={handleGenerateVibe}
              disabled={generatingVibe || !vibePrompt}
              className="w-full bg-violet-600/20 hover:bg-violet-600/30 text-violet-300 py-2 rounded-lg text-sm transition-all disabled:opacity-50 border border-violet-500/20 hover:border-violet-500/40"
            >
              {generatingVibe ? "Scouting..." : "Expand Vibe"}
            </button>
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {song.vibe_cloud?.map((anchor, i) => (
              <button 
                key={i} 
                onClick={() => handleInsertVibe(anchor)}
                className="px-3 py-1 bg-slate-800/40 hover:bg-violet-600/20 hover:border-violet-500/50 hover:text-violet-200 backdrop-blur-sm border border-slate-700/50 rounded-full text-xs text-slate-300 shadow-sm transition-all cursor-pointer text-left"
                title="Click to insert into lyrics"
              >
                {anchor}
              </button>
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
                <button
                  onClick={handleRewrite}
                  disabled={rewriting || !lyrics}
                  className="bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 px-3 py-1.5 rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center gap-2 border border-slate-700/30"
                  title="Rewrite selection"
                >
                  {rewriting ? <Loader2 size={12} className="animate-spin" /> : <RotateCcw size={12} />}
                  Rewrite
                </button>
                <select 
                    value={rhymeScheme}
                    onChange={(e) => setRhymeScheme(e.target.value)}
                    disabled={writingLyrics}
                    className="bg-slate-800/50 text-slate-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-violet-500 border border-slate-700/30"
                >
                    <option value="Free Verse">Free Verse</option>
                    <option value="AABB">AABB</option>
                    <option value="ABAB">ABAB</option>
                    <option value="ABBA">ABBA</option>
                </select>
                <button
                  onClick={handleToggleStress}
                  disabled={analyzingStress || !lyrics}
                  className={`px-3 py-1.5 rounded-lg text-xs transition-all disabled:opacity-50 flex items-center gap-2 border border-slate-700/30 ${
                    showStress 
                      ? "bg-violet-600 text-white shadow-[0_0_10px_rgba(139,92,246,0.5)]" 
                      : "bg-slate-800/50 hover:bg-slate-700/50 text-slate-300"
                  }`}
                >
                  {analyzingStress ? <Loader2 size={12} className="animate-spin" /> : <Activity size={12} />}
                  Stress
                </button>
                <button
                  onClick={handleWriteLyrics}
                  disabled={writingLyrics}
                  className="bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 px-3 py-1.5 rounded-lg text-xs transition-all disabled:opacity-50 flex items-center gap-2 border border-slate-700/30"
                >
                  {writingLyrics ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                  Lyrics Factory
                </button>
            </div>
          </div>
          <div className="flex-1 relative flex overflow-hidden rounded-lg border border-slate-800/50 bg-slate-950/20 shadow-inner">
             <div className="w-10 bg-slate-950/40 backdrop-blur-sm border-r border-slate-800/50 flex flex-col pt-4 items-center text-[10px] text-slate-500 font-mono space-y-[1.15rem] pointer-events-none select-none overflow-hidden">
                {syllableCounts.map((count, i) => (
                  <div key={i} className="h-4 flex items-center justify-center">
                    {count > 0 ? count : ""}
                  </div>
                ))}
             </div>
             {showStress ? (
                 <div className="flex-1 p-4 text-slate-300 font-mono text-sm overflow-y-auto leading-relaxed whitespace-pre-wrap selection:bg-violet-500/30">
                    {renderStressContent(stressContent)}
                 </div>
             ) : (
                 <textarea
                    ref={textareaRef}
                    className="flex-1 bg-transparent p-4 text-slate-200 font-mono text-sm focus:outline-none resize-none leading-relaxed selection:bg-violet-500/30"
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
