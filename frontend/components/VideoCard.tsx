import type { VideoAnalysis } from "@/types";

type VideoCardProps = {
  label: string;
  analysis?: VideoAnalysis;
};

export function VideoCard({ label, analysis }: VideoCardProps) {
  return (
    <article className="rounded-lg border border-zinc-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-zinc-900">{label}</h2>
        <span className="rounded-full bg-zinc-100 px-2 py-1 text-xs text-zinc-600">{analysis?.metadata.platform ?? "Pending"}</span>
      </div>
      <h3 className="min-h-12 text-base font-medium text-zinc-950">{analysis?.metadata.title ?? "Add a URL and analyze"}</h3>
      <p className="mt-2 text-sm text-zinc-600">{analysis?.metadata.creator_name ?? "Creator details will appear after analysis."}</p>
      <dl className="mt-4 grid grid-cols-2 gap-2 text-sm md:grid-cols-3">
        <Metric label="Views" value={analysis?.metadata.views ?? 0} />
        <Metric label="Likes" value={analysis?.metadata.likes ?? 0} />
        <Metric label="Comments" value={analysis?.metadata.comments ?? 0} />
        <Metric label="Followers" value={analysis?.metadata.follower_count ?? "N/A"} />
        <Metric label="Duration" value={formatDuration(analysis?.metadata.duration_seconds)} />
        <Metric label="Engagement" value={`${analysis?.metadata.engagement_rate ?? 0}%`} />
      </dl>
      {analysis?.metadata.upload_date ? <p className="mt-3 text-xs text-zinc-500">Uploaded {analysis.metadata.upload_date}</p> : null}
      {analysis?.metadata.hashtags?.length ? (
        <div className="mt-3 flex flex-wrap gap-1">
          {analysis.metadata.hashtags.slice(0, 8).map((tag) => (
            <span className="rounded-full bg-zinc-100 px-2 py-1 text-xs text-zinc-600" key={tag}>
              {tag}
            </span>
          ))}
        </div>
      ) : null}
      <p className="mt-4 line-clamp-4 text-sm leading-6 text-zinc-600">{analysis?.transcript_preview || "Transcript preview will appear here."}</p>
      <p className="mt-3 text-xs text-zinc-500">{analysis ? `${analysis.chunks.length} transcript chunks indexed` : "No chunks indexed yet"}</p>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-md bg-zinc-50 p-3">
      <dt className="text-xs text-zinc-500">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-zinc-950">{value}</dd>
    </div>
  );
}

function formatDuration(seconds?: number | null) {
  if (!seconds) return "N/A";
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}
