export default function Home() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Welcome to VibeFlow</h1>
        <p className="text-slate-400 text-lg">
          Your AI-powered songwriting studio.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 hover:border-violet-500/50 transition-colors">
          <h2 className="text-xl font-semibold mb-2 text-violet-400">Start Writing</h2>
          <p className="text-slate-400 mb-4">
            Create a new project and use the Vibe Engine to brainstorm sensory details.
          </p>
          <div className="text-sm text-slate-500">
            Click "New Song" in the sidebar to begin.
          </div>
        </div>

        <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 hover:border-violet-500/50 transition-colors">
          <h2 className="text-xl font-semibold mb-2 text-violet-400">Features</h2>
          <ul className="text-slate-400 space-y-2">
            <li>✨ <b>Vibe Cloud:</b> Generate sensory anchors</li>
            <li>📝 <b>Ghostwriter:</b> Draft lyrics with AI</li>
            <li>🎵 <b>Pro Editor:</b> Syllable counting (Coming Soon)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}