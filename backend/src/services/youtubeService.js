import axios from 'axios';
import { YoutubeTranscript } from 'youtube-transcript';
import { config } from '../config.js';
import { withRetry } from '../utils/retry.js';
import { summarizeText } from '../utils/text.js';

const api = axios.create({
  baseURL: 'https://www.googleapis.com/youtube/v3'
});

export async function fetchLatestVideos() {
  const results = [];
  for (const channelId of config.youtubeChannelIds) {
    const search = await withRetry(() => api.get('/search', {
      params: {
        key: config.youtubeApiKey,
        channelId,
        part: 'snippet',
        order: 'date',
        maxResults: 5,
        type: 'video'
      }
    }));

    const ids = search.data.items.map((item) => item.id.videoId).join(',');
    if (!ids) continue;

    const details = await withRetry(() => api.get('/videos', {
      params: { key: config.youtubeApiKey, id: ids, part: 'snippet,statistics' }
    }));

    for (const item of details.data.items) {
      let caption = '';
      try {
        const transcript = await withRetry(() => YoutubeTranscript.fetchTranscript(item.id));
        caption = transcript.map((t) => t.text).join(' ');
      } catch {
        caption = '';
      }

      results.push({
        youtube_id: item.id,
        title: item.snippet.title,
        caption,
        views: Number(item.statistics.viewCount || 0),
        likes: Number(item.statistics.likeCount || 0),
        comments: Number(item.statistics.commentCount || 0),
        summary_short: summarizeText(caption || item.snippet.description, 'short'),
        summary_long: summarizeText(caption || item.snippet.description, 'long'),
        collected_at: new Date().toISOString()
      });
    }
  }

  return results;
}
