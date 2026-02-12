const STOP_WORDS = new Set(['the', 'and', 'a', 'to', 'of', 'is', 'in', 'on', 'for', 'that', 'with', 'it', 'as']);

export function summarizeText(text, level = 'standard', tone = 'neutral') {
  const clean = (text || '').replace(/\s+/g, ' ').trim();
  if (!clean) return '';

  const sentenceLimit = level === 'short' ? 1 : level === 'long' ? 4 : 2;
  const sentences = clean.split(/(?<=[.!?])\s+/).slice(0, sentenceLimit);
  let summary = sentences.join(' ');

  if (tone === 'friendly') summary = `😊 ${summary}`;
  if (tone === 'professional') summary = `요약 리포트: ${summary}`;
  return summary;
}

export function keywordExtract(text, limit = 5) {
  const counts = new Map();
  for (const token of (text || '').toLowerCase().match(/[a-zA-Z가-힣0-9]+/g) || []) {
    if (token.length < 2 || STOP_WORDS.has(token)) continue;
    counts.set(token, (counts.get(token) || 0) + 1);
  }

  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit).map(([word]) => word);
}

export function toDraft({ sourceType, title, summary, level = 'standard' }) {
  return `[${sourceType.toUpperCase()}][${level}] ${title}\n\n${summary}\n\n#자동초안 #MVP`;
}
