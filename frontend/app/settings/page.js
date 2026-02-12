export default function SettingsPage() {
  return (
    <main>
      <h1>설정(Settings)</h1>
      <section className="card">
        <label>YouTube API Key<input placeholder="YOUTUBE_API_KEY" /></label><br /><br />
        <label>Discord Bot Token<input placeholder="DISCORD_BOT_TOKEN" /></label><br /><br />
        <label>Telegram Bot Token<input placeholder="TELEGRAM_BOT_TOKEN" /></label><br /><br />
        <label>RSS 목록<textarea rows={3} placeholder="https://rss1,https://rss2" /></label><br /><br />
        <label>자동 수집 주기(분)<input placeholder="30" /></label><br /><br />
        <button className="primary">저장(실제 값은 env/.env에서 관리)</button>
      </section>
    </main>
  );
}
