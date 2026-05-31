"use client";

import { Link2, Loader2, PlayCircle } from "lucide-react";

type UrlFormProps = {
  videoAUrl: string;
  videoBUrl: string;
  isLoading: boolean;
  onVideoAChange: (value: string) => void;
  onVideoBChange: (value: string) => void;
  onAnalyze: () => void;
};

export function UrlForm(props: UrlFormProps) {
  return (
    <section className="rounded-lg border border-white/80 bg-white/85 p-4 shadow-sm shadow-slate-900/5 backdrop-blur">
      <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-900">
        <PlayCircle className="text-teal-700" size={18} aria-hidden="true" />
        Analyze two videos
      </div>
      <div className="grid gap-3 lg:grid-cols-[1fr_1fr_auto]">
        <UrlInput label="Video A" value={props.videoAUrl} placeholder="Paste YouTube or Instagram URL" onChange={props.onVideoAChange} tone="teal" />
        <UrlInput label="Video B" value={props.videoBUrl} placeholder="Paste YouTube or Instagram URL" onChange={props.onVideoBChange} tone="amber" />
        <button
          className="inline-flex h-[58px] items-center justify-center gap-2 rounded-md bg-slate-950 px-5 text-sm font-semibold text-white shadow-sm shadow-slate-950/20 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400 lg:self-end"
          onClick={props.onAnalyze}
          disabled={props.isLoading}
        >
          {props.isLoading ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <PlayCircle size={18} aria-hidden="true" />}
          {props.isLoading ? "Analyzing" : "Analyze"}
        </button>
      </div>
    </section>
  );
}

function UrlInput({
  label,
  value,
  placeholder,
  tone,
  onChange,
}: {
  label: string;
  value: string;
  placeholder: string;
  tone: "teal" | "amber";
  onChange: (value: string) => void;
}) {
  const iconClass = tone === "teal" ? "text-teal-700" : "text-amber-700";
  const focusClass = tone === "teal" ? "focus-within:border-teal-400 focus-within:ring-teal-100" : "focus-within:border-amber-400 focus-within:ring-amber-100";

  return (
    <label>
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</span>
      <span className={`flex h-[58px] items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 ring-4 ring-transparent transition ${focusClass}`}>
        <Link2 className={iconClass} size={18} aria-hidden="true" />
        <input
          className="min-w-0 flex-1 bg-transparent text-sm text-slate-950 outline-none placeholder:text-slate-400"
          placeholder={placeholder}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      </span>
    </label>
  );
}
