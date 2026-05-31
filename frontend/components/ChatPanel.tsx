"use client";

import { useState } from "react";
import { Bot, Lightbulb, Loader2, MessageCircleQuestion, Send, UserRound } from "lucide-react";
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
    } catch (error) {
      const message = error instanceof Error ? error.message : "Chat request failed";
      setMessages((current) => {
        const updated = [...current];
        updated[updated.length - 1] = { role: "assistant", content: message };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <aside className="flex min-h-[620px] flex-col rounded-lg border border-white/80 bg-slate-950 shadow-xl shadow-slate-900/15 lg:sticky lg:top-6 lg:max-h-[calc(100vh-3rem)]">
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-md bg-teal-400 text-slate-950">
              <Bot size={20} aria-hidden="true" />
            </span>
            <div>
              <h2 className="text-sm font-semibold text-white">Analysis chat</h2>
              <p className="mt-0.5 text-xs text-slate-400">{collectionName ? "Grounded in the latest analysis" : "Analyze videos to unlock chat"}</p>
            </div>
          </div>
          <span className={`h-2.5 w-2.5 rounded-full ${collectionName ? "bg-teal-300" : "bg-slate-600"}`} aria-label={collectionName ? "Ready" : "Not ready"} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.length ? (
          <div className="flex flex-col gap-4">
            {messages.map((chatMessage, index) => (
              <MessageBubble message={chatMessage} isStreaming={isStreaming && index === messages.length - 1 && !chatMessage.content} key={`${chatMessage.role}-${index}`} />
            ))}
          </div>
        ) : (
          <div className="flex h-full min-h-80 flex-col justify-between rounded-md border border-white/10 bg-white/[0.04] p-4">
            <div>
              <div className="flex h-12 w-12 items-center justify-center rounded-md bg-white/10 text-teal-200">
                <MessageCircleQuestion size={24} aria-hidden="true" />
              </div>
              <p className="mt-4 text-sm font-medium text-white">Ask for metrics, comparisons, hooks, or transcript-backed takeaways.</p>
              <p className="mt-2 text-sm leading-6 text-slate-400">Once analysis finishes, answers use the indexed transcript chunks and video metadata.</p>
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {["Which video has more views?", "Compare the hooks", "What drove engagement?"].map((prompt) => (
                <button
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-left text-xs font-medium text-slate-200 transition hover:bg-white/10 disabled:opacity-50"
                  disabled={!collectionName}
                  key={prompt}
                  onClick={() => setMessage(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="mb-2 flex items-center gap-2 text-xs text-slate-400">
          <Lightbulb size={14} aria-hidden="true" />
          Try asking which video won on views, engagement, or retention clues.
        </div>
        <div className="flex gap-2 rounded-md border border-white/10 bg-white/[0.06] p-2 focus-within:border-teal-300/60">
          <input
            className="min-w-0 flex-1 bg-transparent px-2 text-sm text-white outline-none placeholder:text-slate-500"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                sendMessage();
              }
            }}
            placeholder="Ask about the two videos"
          />
          <button
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-teal-400 text-slate-950 transition hover:bg-teal-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            disabled={!collectionName || isStreaming || !message.trim()}
            onClick={sendMessage}
            aria-label="Send message"
          >
            {isStreaming ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <Send size={18} aria-hidden="true" />}
          </button>
        </div>
      </div>
    </aside>
  );
}

function MessageBubble({
  message,
  isStreaming,
}: {
  message: { role: "user" | "assistant"; content: string };
  isStreaming: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser ? (
        <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-teal-400 text-slate-950">
          <Bot size={17} aria-hidden="true" />
        </span>
      ) : null}
      <div className={`max-w-[86%] rounded-lg px-4 py-3 text-sm leading-6 shadow-sm ${isUser ? "bg-amber-300 text-slate-950" : "bg-white text-slate-700"}`}>
        {message.content || (isStreaming ? "Thinking..." : "")}
      </div>
      {isUser ? (
        <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-amber-300 text-slate-950">
          <UserRound size={17} aria-hidden="true" />
        </span>
      ) : null}
    </div>
  );
}
