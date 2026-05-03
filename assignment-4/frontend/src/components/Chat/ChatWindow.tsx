import { useEffect, useRef, useState } from "react";
import type { Message } from "../../hooks/useChat";
import ChatMessage from "./ChatMessage";

interface Props {
  messages: Message[];
  loading: boolean;
  onApprovalResolved: (approvalId: string) => void;
  onSend: (text: string) => void;
}

export default function ChatWindow({ messages, loading, onApprovalResolved, onSend }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState("");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    onSend(text);
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <div className="text-center text-zinc-500 mt-24 text-sm">
            Click a skill in the sidebar or type a message to begin.
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} onApprovalResolved={onApprovalResolved} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-zinc-800 px-4 py-3 flex gap-3 items-end">
        <textarea
          className="flex-1 bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2 text-sm text-zinc-100 resize-none focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-zinc-500"
          rows={2}
          placeholder={loading ? "Waiting for model response…" : "Type a message or click a skill to start…"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-sm rounded-xl transition"
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
