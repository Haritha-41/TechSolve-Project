import type { AnalyzeVideosResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function analyzeVideos(videoAUrl: string, videoBUrl: string): Promise<AnalyzeVideosResponse> {
  const response = await fetch(`${API_URL}/api/videos/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      video_a: { label: "Video A", url: videoAUrl },
      video_b: { label: "Video B", url: videoBUrl },
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Video analysis failed" }));
    throw new Error(error.detail ?? "Video analysis failed");
  }

  return response.json();
}

export async function streamChat(collectionName: string, message: string, onToken: (token: string) => void) {
  const response = await fetch(`${API_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ collection_name: collectionName, message, session_id: "default" }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Chat request failed" }));
    throw new Error(error.detail ?? "Chat request failed");
  }

  if (!response.body) {
    throw new Error("Streaming is not available");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      parseSseBuffer(buffer, onToken);
      break;
    }
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    buffer = parseSseBuffer(buffer, onToken);
  }
}

function parseSseBuffer(buffer: string, onToken: (token: string) => void) {
  const events = buffer.split("\n\n");
  const remainder = events.pop() ?? "";

  for (const event of events) {
    const dataLines: string[] = [];
    for (const line of event.split("\n")) {
      if (line.startsWith("data: ") && line !== "data: [done]") {
        dataLines.push(line.slice(6));
      }
    }
    if (dataLines.length) {
      onToken(dataLines.join("\n"));
    }
  }

  return remainder;
}
