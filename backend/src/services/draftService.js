import { summarizeText, toDraft } from '../utils/text.js';

export function buildDraftsFromVideos(videos, tone = 'neutral') {
  return videos.map((video) => {
    const summary = summarizeText(video.caption || video.title, 'standard', tone);
    return {
      source_type: 'youtube',
      draft_text: toDraft({ sourceType: 'youtube', title: video.title, summary }),
      created_at: new Date().toISOString(),
      published: false
    };
  });
}

export function buildDraftsFromNews(news, tone = 'neutral') {
  return news.map((item) => {
    const summary = summarizeText(item.raw_text || item.title, 'standard', tone);
    return {
      source_type: 'news',
      draft_text: toDraft({ sourceType: 'news', title: item.title, summary }),
      created_at: new Date().toISOString(),
      published: false
    };
  });
}
