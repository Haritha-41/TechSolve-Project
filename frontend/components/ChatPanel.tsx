"use client";

import { useState } from "react";
import { streamChat } from "@/lib/api";

type ChatPanelProps = {
  collectionName?: string;
};

export function ChatPanel({ collectionName }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [stream, setStream] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  async function sendMessage() {
    if (!collectionName || !message.trim()) return;
    setIsStreaming(true);
    setStream("");
    try {
      await streamChat(collectionName, message, (token) => setStream((current) => current + token));
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-4">
      <h2 className="text-sm font-semibold text-zinc-950">Chat</h2>
      <div className="mt-3 min-h-44 rounded-md bg-zinc-50 p-3 text-sm leading-6 text-zinc-700">{stream || "Analyze videos, then ask for comparisons, themes, hooks, or engagement insights."}</div>
      <div className="mt-3 flex gap-2">
        <input className="h-10 flex-1 rounded-md border border-zinc-300 px-3 text-sm" value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask about the two videos" />
        <button className="h-10 rounded-md bg-zinc-950 px-4 text-sm font-medium text-white disabled:bg-zinc-400" disabled={!collectionName || isStreaming} onClick={sendMessage}>
          Send
        </button>
      </div>
    </section>
  );
}
