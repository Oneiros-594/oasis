
"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(text: string) {
    const message = text.trim();

    if (!message || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: message },
    ]);
    setPrompt("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned HTTP ${response.status}`);
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.reply },
      ]);
    } catch {
      setError(
        "Couldn't reach Oasis. Check that the FastAPI backend and Ollama are running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="oasis-shell">
      <aside className="sidebar">
        <div className="brand">
          <img
            src="/oasis-icon-transparent.png"
            alt="Oasis logo"
            className="brand-logo"
          />
          <span>OASIS</span>
        </div>

        <button
          className="new-chat"
          onClick={() => {
            setMessages([]);
            setPrompt("");
            setError("");
          }}
        >
          <span>＋</span> New conversation
        </button>

        <p className="nav-label">YOUR SPACE</p>
        <button className="nav-item active">
          <span>◉</span> AI Assistant
        </button>
        <button className="nav-item">
          <span>✧</span> Explore worlds
        </button>
        <button className="nav-item">
          <span>◷</span> Recent activity
        </button>

        <div className="sidebar-bottom">
          <div className="profile-avatar">A</div>
          <div>
            <strong>Explorer</strong>
            <p>Personal workspace</p>
          </div>
          <span className="status-dot" />
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="breadcrumb">OASIS</span>
            <span className="breadcrumb-separator"> / </span>
            <span className="breadcrumb-current">Assistant</span>
          </div>
          <div className="connection">
            <span className="status-dot" />
            Local AI workspace
          </div>
        </header>

        <div className="welcome">
          {messages.length === 0 ? (
            <>
              <div className="hero-brand-mark">
                <img
                  src="/oasis-icon-transparent.png"
                  alt="Oasis orbital logo"
                  className="hero-brand-logo"
                />
              </div>

              <p className="eyebrow">YOUR SPACE TO IMAGINE</p>
              <h1>
                A world of ideas,
                <br />
                <span>waiting for you.</span>
              </h1>

              <p className="welcome-description">
                Meet your AI companion. Explore ideas, solve problems,
                and start creating worlds that exist only in your imagination.
              </p>

              <div className="suggestions">
                <button onClick={() => setPrompt("Help me learn something new")}>
                  <span>✧</span> Learn something new
                </button>
                <button onClick={() => setPrompt("Help me brainstorm a project")}>
                  <span>⌘</span> Brainstorm a project
                </button>
                <button onClick={() => setPrompt("Help me imagine a new world")}>
                  <span>◈</span> Imagine a new world
                </button>
              </div>
            </>
          ) : (
            <div className="chat-messages" aria-live="polite">
              {messages.map((message, index) => (
                <div
                  className={`chat-message ${message.role}`}
                  key={`${index}-${message.role}`}
                >
                  <strong>
                    {message.role === "user" ? "You" : "Oasis"}
                  </strong>
                  <p>{message.content}</p>
                </div>
              ))}
              {loading && (
                <div className="chat-message assistant">
                  <strong>Oasis</strong>
                  <p>Thinking...</p>
                </div>
              )}
              <div />
            </div>
          )}

          {error && <p role="alert">{error}</p>}

          <form
            className="prompt-box"
            onSubmit={(event) => {
              event.preventDefault();
              void sendMessage(prompt);
            }}
          >
            
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();

                if (prompt.trim() && !loading) {
                  event.currentTarget.form?.requestSubmit();
                }
              }
            }}
            placeholder="Ask Oasis anything, or describe a world..."
            rows={2}
          />

            
            <div className="prompt-footer">
              <span>✧ &nbsp; Your imagination is the limit</span>
              <button
                type="submit"
                disabled={!prompt.trim() || loading}
                aria-label="Send message"
              >
                {loading ? "…" : "↑"}
              </button>
            </div>
          </form>

          <p className="disclaimer">
            Powered by your local AI model. No paid API required.
          </p>
        </div>

        <footer className="workspace-footer">
          <span>OASIS © 2026</span>
          <span>Built for curious minds.</span>
        </footer>
      </section>
    </main>
  );
}
