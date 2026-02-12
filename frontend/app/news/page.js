async function getNews() {
  const base = process.env.NEXT_PUBLIC_API_BASE;
  return fetch(`${base}/news`, { cache: 'no-store' }).then((r) => r.json()).catch(() => []);
}

export default async function NewsPage() {
  const news = await getNews();
  return (
    <main>
      <h1>뉴스 리스트</h1>
      {news.map((item) => (
        <article className="card" key={item.id}>
          <p className="small">{item.source} · {new Date(item.collected_at).toLocaleString()}</p>
          <h3>{item.title}</h3>
          <p>{item.summary_short}</p>
          <button className="primary">발행</button>
        </article>
      ))}
    </main>
  );
}
