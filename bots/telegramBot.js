import dotenv from 'dotenv';
import TelegramBot from 'node-telegram-bot-api';

dotenv.config({ path: '../env/.env' });

const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { polling: true });

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, '자동화 봇이 연결되었습니다.');
});

bot.onText(/\/draft (.+)/, (msg, match) => {
  bot.sendMessage(msg.chat.id, `초안 저장 후보: ${match[1]}`);
});
