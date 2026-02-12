import { ensureDbConfig, supabase } from '../services/supabaseClient.js';
import { fetchLatestVideos } from '../services/youtubeService.js';
import { fetchRssNews, normalizeNews } from '../services/newsService.js';
import { fetchDiscordNews } from '../services/discordService.js';
import { buildDraftsFromNews, buildDraftsFromVideos } from '../services/draftService.js';

export async function runCollectors() {
  ensureDbConfig();

  const [videos, rssNews, discordNews] = await Promise.all([
    fetchLatestVideos().catch(() => []),
    fetchRssNews().catch(() => []),
    fetchDiscordNews().catch(() => [])
  ]);

  const news = normalizeNews([...rssNews, ...discordNews]);

  if (videos.length > 0) {
    await supabase.from('videos').upsert(videos, { onConflict: 'youtube_id' });
  }
  if (news.length > 0) {
    await supabase.from('news').insert(news);
  }

  const drafts = [...buildDraftsFromVideos(videos), ...buildDraftsFromNews(news)];
  if (drafts.length > 0) {
    await supabase.from('drafts').insert(drafts);
  }

  return {
    videos: videos.length,
    news: news.length,
    drafts: drafts.length
  };
}
