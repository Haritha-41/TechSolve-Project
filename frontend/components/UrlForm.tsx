"use client";

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
    <section className="border-b border-zinc-200 bg-white">
      <div className="mx-auto grid max-w-6xl gap-3 px-6 py-5 md:grid-cols-[1fr_1fr_auto]">
        <input className="h-11 rounded-md border border-zinc-300 px-3 text-sm" placeholder="Video A URL, YouTube or Instagram" value={props.videoAUrl} onChange={(event) => props.onVideoAChange(event.target.value)} />
        <input className="h-11 rounded-md border border-zinc-300 px-3 text-sm" placeholder="Video B URL, YouTube or Instagram" value={props.videoBUrl} onChange={(event) => props.onVideoBChange(event.target.value)} />
        <button className="h-11 rounded-md bg-zinc-950 px-5 text-sm font-medium text-white disabled:bg-zinc-400" onClick={props.onAnalyze} disabled={props.isLoading}>
          {props.isLoading ? "Analyzing" : "Analyze"}
        </button>
      </div>
    </section>
  );
}
