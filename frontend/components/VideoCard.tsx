import type { VideoAnalysis } from "@/types";
import type { ReactNode } from "react";
import { BarChart3, CalendarDays, Clock3, Eye, Heart, MessageCircle, Radio, Users } from "lucide-react";

type VideoCardProps = {
  label: string;
  accent: "teal" | "amber";
  analysis?: VideoAnalysis;
};

export function VideoCard({ label, accent, analysis }: VideoCardProps) {
  const tone = accent === "teal" ? styles.teal : styles.amber;

  return (
    <article className="overflow-hidden rounded-lg border border-white/80 bg-white/90 shadow-sm shadow-slate-900/5 backdrop-blur">
      <div className={`h-1.5 ${tone.bar}`} />
      <div className="p-4">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className={`flex h-9 w-9 items-center justify-center rounded-md ${tone.iconBg} ${tone.iconText}`}>
              <Radio size={18} aria-hidden="true" />
            </span>
            <div>
              <h2 className="text-sm font-semibold text-slate-950">{label}</h2>
              <p className="text-xs text-slate-500">{analysis ? "Indexed and ready" : "Waiting for URL"}</p>
            </div>
          </div>
          <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${analysis ? tone.badge : "bg-slate-100 text-slate-500"}`}>
            {analysis?.metadata.platform ?? "Pending"}
          </span>
        </div>

        <h3 className="min-h-14 text-base font-semibold leading-6 text-slate-950">{analysis?.metadata.title ?? "Add a URL and run analysis"}</h3>
        <p className="mt-2 text-sm text-slate-600">{analysis?.metadata.creator_name ?? "Creator details will appear after analysis."}</p>

        <dl className="mt-4 grid grid-cols-2 gap-2 text-sm sm:grid-cols-3 xl:grid-cols-2 2xl:grid-cols-3">
          <Metric icon={<Eye size={16} aria-hidden="true" />} label="Views" value={formatMetric(analysis?.metadata.views)} tone={accent} />
          <Metric icon={<Heart size={16} aria-hidden="true" />} label="Likes" value={formatMetric(analysis?.metadata.likes)} tone={accent} />
          <Metric icon={<MessageCircle size={16} aria-hidden="true" />} label="Comments" value={formatMetric(analysis?.metadata.comments)} tone={accent} />
          <Metric icon={<Users size={16} aria-hidden="true" />} label="Followers" value={formatMetric(analysis?.metadata.follower_count)} tone={accent} />
          <Metric icon={<Clock3 size={16} aria-hidden="true" />} label="Duration" value={formatDuration(analysis?.metadata.duration_seconds)} tone={accent} />
          <Metric icon={<BarChart3 size={16} aria-hidden="true" />} label="Engagement" value={formatEngagement(analysis?.metadata.engagement_rate)} tone={accent} />
        </dl>

        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
          {analysis?.metadata.upload_date ? (
            <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1">
              <CalendarDays size={13} aria-hidden="true" />
              {analysis.metadata.upload_date}
            </span>
          ) : null}
          <span className="rounded-full bg-slate-100 px-2.5 py-1">{analysis ? `${analysis.chunks.length} chunks indexed` : "No chunks yet"}</span>
        </div>

        {analysis?.metadata.hashtags?.length ? (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {analysis.metadata.hashtags.slice(0, 8).map((tag) => (
              <span className={`rounded-full px-2 py-1 text-xs font-medium ${tone.softTag}`} key={tag}>
                {tag}
              </span>
            ))}
          </div>
        ) : null}

        <div className="mt-4 rounded-md border border-slate-100 bg-slate-50/80 p-3">
          <p className="line-clamp-4 text-sm leading-6 text-slate-600">{analysis?.transcript_preview || "Transcript preview will appear here after the backend extracts or transcribes audio."}</p>
        </div>
      </div>
    </article>
  );
}

function Metric({ icon, label, value, tone }: { icon: ReactNode; label: string; value: number | string; tone: "teal" | "amber" }) {
  const toneClass = tone === "teal" ? "text-teal-700 bg-teal-50" : "text-amber-700 bg-amber-50";

  return (
    <div className="rounded-md border border-slate-100 bg-white p-3 shadow-sm shadow-slate-900/[0.03]">
      <dt className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
        <span className={`flex h-6 w-6 items-center justify-center rounded-md ${toneClass}`}>{icon}</span>
        {label}
      </dt>
      <dd className="mt-2 truncate text-sm font-bold text-slate-950">{value}</dd>
    </div>
  );
}

function formatDuration(seconds?: number | null) {
  if (!seconds) return "N/A";
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

function formatMetric(value?: number | null) {
  if (value === undefined || value === null) return "N/A";
  return new Intl.NumberFormat("en").format(value);
}

function formatEngagement(value?: number | null) {
  if (value === undefined || value === null) return "N/A";
  return `${value}%`;
}

const styles = {
  teal: {
    bar: "bg-teal-500",
    iconBg: "bg-teal-50",
    iconText: "text-teal-700",
    badge: "bg-teal-50 text-teal-800",
    softTag: "bg-teal-50 text-teal-700",
  },
  amber: {
    bar: "bg-amber-500",
    iconBg: "bg-amber-50",
    iconText: "text-amber-700",
    badge: "bg-amber-50 text-amber-800",
    softTag: "bg-amber-50 text-amber-700",
  },
};
