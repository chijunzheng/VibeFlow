export const API_URL = "http://localhost:8000";

export interface Song {
  id: number;
  title: string;
  vibe_cloud?: string[];
  content?: Record<string, any>;
  thought_sig?: string;
  created_at: string;
  updated_at: string;
}

export async function fetchSongs(): Promise<Song[]> {
  const res = await fetch(`${API_URL}/songs/`);
  if (!res.ok) throw new Error("Failed to fetch songs");
  return res.json();
}

export async function fetchSong(id: number): Promise<Song> {
  const res = await fetch(`${API_URL}/songs/${id}`);
  if (!res.ok) throw new Error("Failed to fetch song");
  return res.json();
}

export async function createSong(title: string): Promise<Song> {
  const res = await fetch(`${API_URL}/songs/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to create song");
  return res.json();
}

export async function generateVibe(id: number, prompt: string): Promise<Song> {
  const res = await fetch(`${API_URL}/songs/${id}/generate_vibe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to generate vibe");
  return res.json();
}

export async function writeLyrics(id: number, style: string = "Modern"): Promise<Song> {
  const res = await fetch(`${API_URL}/songs/${id}/write_lyrics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });
  if (!res.ok) throw new Error("Failed to write lyrics");
  return res.json();
}

export const getStreamLyricsUrl = (id: number, style: string = "Modern") => 
  `${API_URL}/songs/${id}/write_lyrics/stream?style=${encodeURIComponent(style)}`;

export async function countSyllables(text: string): Promise<number[]> {
  const res = await fetch(`${API_URL}/utils/syllables`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Failed to count syllables");
  return res.json();
}
