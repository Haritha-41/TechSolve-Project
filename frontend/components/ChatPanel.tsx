"use client";

import { useState } from "react";
import { streamChat } from "@/lib/api";

type ChatPanelProps = {
  collectionName?: string;
};

export function ChatPanel({ collectionName }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  async function sendMessage() {
    if (!collectionName || !message.trim()) return;
    const nextMessage = message.trim();
    setMessage("");
    setIsStreaming(true);
    setMessages((current) => [...current, { role: "user", content: nextMessage }, { role: "assistant", content: "" }]);
    try {
      await streamChat(collectionName, nextMessage, (token) => {
        setMessages((current) => {
          const updated = [...current];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = { ...last, content: last.content + token };
          return updated;
        });
      });
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-4">
      <h2 className="text-sm font-semibold text-zinc-950">Chat</h2>
      <div className="mt-3 flex min-h-56 flex-col gap-3 rounded-md bg-zinc-50 p-3 text-sm leading-6 text-zinc-700">
        {messages.length ? (
          messages.map((chatMessage, index) => (
            <div className={chatMessage.role === "user" ? "font-medium text-zinc-950" : "whitespace-pre-wrap text-zinc-700"} key={`${chatMessage.role}-${index}`}>
              {chatMessage.content || "Streaming..."}
            </div>
          ))
        ) : (
          <p>Analyze videos, then ask for comparisons, hooks, engagement insights, or creator statistics.</p>
        )}
      </div>
      <div className="mt-3 flex gap-2">
        <input className="h-10 flex-1 rounded-md border border-zinc-300 px-3 text-sm" value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask about the two videos" />
        <button className="h-10 rounded-md bg-zinc-950 px-4 text-sm font-medium text-white disabled:bg-zinc-400" disabled={!collectionName || isStreaming} onClick={sendMessage}>
          Send
        </button>
      </div>
    </section>
  );
}
