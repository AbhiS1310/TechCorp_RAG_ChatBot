export default function Header() {
  return (
    <header className="border-b border-ink/10 bg-sky/60">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div>
          <p className="font-display text-2xl text-moss">TechCorp HR Intelligence</p>
          <p className="text-sm text-ink/70">RAG chatbot for policy clarity</p>
        </div>
        <div className="rounded-full bg-amber/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-moss">
          Internal
        </div>
      </div>
    </header>
  );
}
