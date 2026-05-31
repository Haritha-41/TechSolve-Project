"use client";

import { useState } from "react";
import { Activity, MessageSquareText, Sparkles } from "lucide-react";
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
    <main className="min-h-screen">
      <header className="border-b border-white/70 bg-white/75 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-teal-600 text-white shadow-sm shadow-teal-900/15">
              <MessageSquareText size={22} aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold tracking-normal text-slate-950">TechSolve Test</h1>
              <p className="mt-1 text-sm text-slate-600">Compare short-form videos with transcript-grounded answers and creator metrics.</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-medium text-slate-600">
            <span className="inline-flex items-center gap-1 rounded-full border border-teal-200 bg-teal-50 px-3 py-1.5 text-teal-800">
              <Activity size={14} aria-hidden="true" />
              Live metrics
            </span>
            <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-amber-800">
              <Sparkles size={14} aria-hidden="true" />
              Gemini chat
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-5 px-5 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_420px]">
        <section className="space-y-5">
          <UrlForm videoAUrl={videoAUrl} videoBUrl={videoBUrl} isLoading={isLoading} onVideoAChange={setVideoAUrl} onVideoBChange={setVideoBUrl} onAnalyze={handleAnalyze} />
          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {error}
            </div>
          ) : null}
          <div className="grid gap-4 xl:grid-cols-2">
            <VideoCard label="Video A" accent="teal" analysis={result?.videos[0]} />
            <VideoCard label="Video B" accent="amber" analysis={result?.videos[1]} />
          </div>
        </section>
        <ChatPanel collectionName={result?.collection_name} />
      </div>
    </main>
  );
}
