async function getVideos() {
  const base = process.env.NEXT_PUBLIC_API_BASE;
  return fetch(`${base}/videos`, { cache: 'no-store' }).then((r) => r.json()).catch(() => []);
}

export default async function YoutubePage() {
  const videos = await getVideos();

  return (
    <main>
      <h1>YouTube 리스트</h1>
      {videos.map((video) => (
        <article key={video.id || video.youtube_id} className="card">
          <p className="small">수집: {new Date(video.collected_at).toLocaleString()}</p>
          <h3>{video.title}</h3>
          <p>조회수 {video.views} · 좋아요 {video.likes} · 댓글 {video.comments}</p>
          <details><summary>요약 보기</summary><p>{video.summary_short}</p></details>
          <button className="primary">초안 생성 버튼(자동 생성됨)</button>
        </article>
      ))}
    </main>
  );
}
