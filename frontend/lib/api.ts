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
    throw new Error("Video analysis failed");
  }

  return response.json();
}

export async function streamChat(collectionName: string, message: string, onToken: (token: string) => void) {
  const response = await fetch(`${API_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ collection_name: collectionName, message, session_id: "default" }),
  });

  if (!response.body) {
    throw new Error("Streaming is not available");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onToken(decoder.decode(value));
  }
}
