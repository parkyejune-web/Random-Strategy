async function getKpi() {
  const base = process.env.NEXT_PUBLIC_API_BASE;
  const [videos, news, drafts] = await Promise.all([
    fetch(`${base}/videos`, { cache: 'no-store' }).then((r) => r.json()).catch(() => []),
    fetch(`${base}/news`, { cache: 'no-store' }).then((r) => r.json()).catch(() => []),
    fetch(`${base}/drafts`, { cache: 'no-store' }).then((r) => r.json()).catch(() => [])
  ]);
  return { videos, news, drafts };
}

export default async function HomePage() {
  const { videos, news, drafts } = await getKpi();
  return (
    <main>
      <h1>자동화 대시보드</h1>
      <div className="grid">
        <section className="card"><h3>오늘 수집 영상</h3><p>{videos.length}</p></section>
        <section className="card"><h3>오늘 수집 뉴스</h3><p>{news.length}</p></section>
        <section className="card"><h3>초안 개수</h3><p>{drafts.length}</p></section>
        <section className="card"><h3>자동화 상태</h3><p>RUNNING</p></section>
      </div>
    </main>
  );
}
