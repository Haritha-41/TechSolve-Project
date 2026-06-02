export type VideoMetadata = {
  title: string;
  platform: string;
  url: string;
  creator_name: string;
  follower_count?: number | null;
  likes?: number | null;
  comments?: number | null;
  views?: number | null;
  upload_date?: string | null;
  duration_seconds?: number | null;
  hashtags: string[];
  engagement_rate?: number | null;
};

export type TranscriptChunk = {
  chunk_id: string;
  video_label: string;
  source_video: "A" | "B";
  creator_name: string;
  video_url: string;
  text: string;
  start_seconds?: number | null;
  end_seconds?: number | null;
};

export type VideoAnalysis = {
  metadata: VideoMetadata;
  transcript_preview: string;
  transcript: string;
  chunks: TranscriptChunk[];
};

export type AnalyzeVideosResponse = {
  videos: VideoAnalysis[];
  collection_name: string;
};
