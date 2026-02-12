import { Client, GatewayIntentBits } from 'discord.js';
import { config } from '../config.js';
import { summarizeText } from '../utils/text.js';

export async function fetchDiscordNews(limit = 20) {
  if (!config.discordToken || config.discordChannelIds.length === 0) return [];

  const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

  return new Promise((resolve) => {
    const timeout = setTimeout(async () => {
      await client.destroy();
      resolve([]);
    }, 15000);

    client.once('ready', async () => {
      const rows = [];
      try {
        for (const channelId of config.discordChannelIds) {
          const channel = await client.channels.fetch(channelId);
          if (!channel?.isTextBased()) continue;
          const messages = await channel.messages.fetch({ limit });
          messages.forEach((msg) => {
            if (!msg.content) return;
            rows.push({
              source: `discord:${channelId}`,
              title: msg.content.slice(0, 80),
              raw_text: msg.content,
              summary_short: summarizeText(msg.content, 'short'),
              summary_long: summarizeText(msg.content, 'long'),
              collected_at: msg.createdAt.toISOString()
            });
          });
        }
      } finally {
        clearTimeout(timeout);
        await client.destroy();
      }
      resolve(rows);
    });

    client.login(config.discordToken).catch(async () => {
      clearTimeout(timeout);
      await client.destroy();
      resolve([]);
    });
  });
}
