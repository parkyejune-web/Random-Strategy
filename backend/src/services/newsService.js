import Parser from 'rss-parser';
import { config } from '../config.js';
import { summarizeText } from '../utils/text.js';
import { withRetry } from '../utils/retry.js';

const parser = new Parser();

export async function fetchRssNews() {
  const rows = [];
  for (const feedUrl of config.rssFeeds) {
    const feed = await withRetry(() => parser.parseURL(feedUrl));
    for (const item of (feed.items || []).slice(0, 10)) {
      const text = `${item.title || ''} ${item.contentSnippet || ''}`;
      rows.push({
        source: `rss:${feed.title || feedUrl}`,
        title: item.title || 'untitled',
        raw_text: text,
        summary_short: summarizeText(text, 'short'),
        summary_long: summarizeText(text, 'long'),
        collected_at: item.isoDate || new Date().toISOString()
      });
    }
  }
  return rows;
}

export function normalizeNews(rows = []) {
  const seen = new Set();
  return rows
    .filter((row) => {
      const key = `${row.title}-${new Date(row.collected_at).toDateString()}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a, b) => new Date(b.collected_at) - new Date(a.collected_at));
}
