import dotenv from 'dotenv';

dotenv.config({ path: '../../env/.env' });
dotenv.config();

export const config = {
  port: Number(process.env.BACKEND_PORT || 4000),
  supabaseUrl: process.env.SUPABASE_URL || '',
  supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY || '',
  youtubeApiKey: process.env.YOUTUBE_API_KEY || '',
  youtubeChannelIds: (process.env.YOUTUBE_CHANNEL_IDS || '').split(',').map((v) => v.trim()).filter(Boolean),
  rssFeeds: (process.env.RSS_FEEDS || '').split(',').map((v) => v.trim()).filter(Boolean),
  discordToken: process.env.DISCORD_BOT_TOKEN || '',
  discordChannelIds: (process.env.DISCORD_CHANNEL_IDS || '').split(',').map((v) => v.trim()).filter(Boolean),
  telegramToken: process.env.TELEGRAM_BOT_TOKEN || '',
  telegramChatId: process.env.TELEGRAM_CHAT_ID || '',
  autoCollectMinutes: Number(process.env.AUTO_COLLECT_MINUTES || 30)
};
