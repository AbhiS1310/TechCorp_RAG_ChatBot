import { useState, useEffect, useRef } from "react";
import { sendChat } from "../services/api.js";

export default function ChatUI() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Ref to track the bottom of the messages list
  const messagesEndRef = useRef(null);

  // Auto-scroll to the latest message whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;

    const newMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, newMessage]);
    setLoading(true);

    try {
      const response = await sendChat(query);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Unable to reach the backend. Please try again.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  return (
    <section className="rounded-3xl border border-ink/10 bg-white/70 p-6 shadow-[0_20px_60px_-45px_rgba(15,61,46,0.6)]">
      <h2 className="font-display text-xl text-moss">Policy Chat</h2>
      <p className="mt-1 text-sm text-ink/70">
        Ask about HR policies. Responses are grounded in the latest documented truth.
      </p>

      {/* Messages container (scrollable) */}
      <div className="mt-6 max-h-[420px] overflow-y-auto space-y-4 pr-1">
        {messages.length === 0 && (
          <div className="rounded-2xl border border-dashed border-ink/20 bg-stone/40 p-6 text-sm text-ink/60">
            Try: “Can I work fully remotely?” or “Can I work remotely this Friday?”
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`rounded-2xl p-4 ${
              message.role === "user"
                ? "bg-moss text-white"
                : "bg-sky/60 text-ink"
            }`}
          >
            <p className="whitespace-pre-line text-sm leading-relaxed">
              {message.content}
            </p>

            {message.role === "assistant" && message.sources?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {message.sources.map((source) => (
                  <span
                    key={source}
                    className="rounded-full border border-ink/20 bg-white/80 px-3 py-1 text-xs font-medium text-ink"
                  >
                    {source}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Invisible anchor element for auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      <form className="mt-6 flex flex-col gap-3" onSubmit={handleSubmit}>
        <textarea
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          rows={3}
          placeholder="Ask a policy question..."
          className="w-full resize-none rounded-2xl border border-ink/20 bg-white px-4 py-3 text-sm focus:border-moss focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center rounded-full bg-moss px-5 py-2 text-sm font-semibold text-white transition hover:bg-moss/90 disabled:cursor-not-allowed disabled:bg-moss/60"
        >
          {loading ? "Thinking..." : "Send question"}
        </button>
      </form>
    </section>
  );
}