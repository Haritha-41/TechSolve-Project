export type VideoInput = {
  label: string;
  url: string;
};

export type VideoMetadata = {
  title: string;
  platform: string;
  url: string;
  likes: number;
  comments: number;
  views: number;
  engagement_rate: number;
};

export type TranscriptChunk = {
  chunk_id: string;
  video_label: string;
  text: string;
};

export type VideoAnalysis = {
  metadata: VideoMetadata;
  transcript_preview: string;
  chunks: TranscriptChunk[];
};

export type AnalyzeVideosResponse = {
  videos: VideoAnalysis[];
  collection_name: string;
};
