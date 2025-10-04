import { useEffect, useRef, useState } from "react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! How can I help?." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const inputRef = useRef(null);
  const newChat = () => {
    setMessages([
      { role: "assistant", content: "Hi! How can I help." },
    ]);
    setInput("");
    setErr(null);
    inputRef.current?.focus();
  }

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setLoading(true);
    setErr(null);
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");

    try {
      const res = await fetch(`/api/chat?query=${encodeURIComponent(q)}`, {
        method: "POST",
      });

      let answer;
      if (res.headers.get("content-type")?.includes("application/json")) {
        const data = await res.json();
        answer = typeof data === "string" ? data : JSON.stringify(data);
      } else {
        answer = await res.text();
        if (/^".*"$/.test(answer)) answer = JSON.parse(answer);
      }

      if (!res.ok) throw new Error(answer || `HTTP ${res.status}`);
      setMessages((m) => [...m, { role: "assistant", content: String(answer) }]);
    } catch (e) {
      const msg =
        e && typeof e === "object" && "message" in e ? e.message : "Request failed";
      setErr(msg);
      setMessages((m) => [...m, { role: "assistant", content: `Error: ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="chat">
      <header className="chat__header">
        <h1>Purdue RAG Chat</h1>
        <button className="new-chat" onClick={newChat} disabled={loading}> New chat </button>
      </header>

      <main className="chat__messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <div className="bubble">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="msg assistant">
            <div className="bubble">Thinking…</div>
          </div>
        )}
        <div ref={endRef} />
      </main>

      <footer className="chat__input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message. Enter to send, Shift+Enter for newline"
          rows={1}
          onKeyDown={onKeyDown}
        />
        <button onClick={send} disabled={loading || !input.trim()}>
          {loading ? "Sending…" : "Send"}
        </button>
      </footer>

      {err && <div className="chat__error">{err}</div>}
    </div>
  );
}