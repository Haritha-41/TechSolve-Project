"use client";

import { useState } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import { UrlForm } from "@/components/UrlForm";
import { VideoCard } from "@/components/VideoCard";
import { analyzeVideos } from "@/lib/api";
import type { AnalyzeVideosResponse } from "@/types";

export default function Home() {
  const [videoAUrl, setVideoAUrl] = useState("");
  const [videoBUrl, setVideoBUrl] = useState("");
  const [result, setResult] = useState<AnalyzeVideosResponse>();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleAnalyze() {
    if (!videoAUrl.trim() || !videoBUrl.trim()) {
      setError("Add both video URLs before analyzing.");
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      setResult(await analyzeVideos(videoAUrl, videoBUrl));
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "Unable to analyze videos");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5">
          <h1 className="text-2xl font-semibold tracking-normal text-zinc-950">SocialSense RAG</h1>
          <p className="mt-1 text-sm text-zinc-600">Compare one YouTube video and one Instagram Reel with transcript-grounded chat.</p>
        </div>
      </header>
      <UrlForm videoAUrl={videoAUrl} videoBUrl={videoBUrl} isLoading={isLoading} onVideoAChange={setVideoAUrl} onVideoBChange={setVideoBUrl} onAnalyze={handleAnalyze} />
      <div className="mx-auto grid max-w-6xl gap-5 px-6 py-6 lg:grid-cols-[1fr_380px]">
        <section className="grid gap-4 md:grid-cols-2">
          <VideoCard label="Video A" analysis={result?.videos[0]} />
          <VideoCard label="Video B" analysis={result?.videos[1]} />
        </section>
        <ChatPanel collectionName={result?.collection_name} />
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </div>
    </main>
  );
}
