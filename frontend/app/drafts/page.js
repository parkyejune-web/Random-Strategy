'use client';

import { useEffect, useState } from 'react';

const base = process.env.NEXT_PUBLIC_API_BASE;

export default function DraftsPage() {
  const [drafts, setDrafts] = useState([]);

  async function load() {
    const data = await fetch(`${base}/drafts`).then((r) => r.json()).catch(() => []);
    setDrafts(data);
  }

  useEffect(() => { load(); }, []);

  async function togglePublish(draft) {
    await fetch(`${base}/drafts/${draft.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ draft_text: draft.draft_text, published: !draft.published })
    });
    load();
  }

  async function remove(id) {
    await fetch(`${base}/drafts/${id}`, { method: 'DELETE' });
    load();
  }

  return (
    <main>
      <h1>자동 초안</h1>
      {drafts.map((draft) => (
        <article className="card" key={draft.id}>
          <p className="small">{draft.source_type} · {new Date(draft.created_at).toLocaleString()}</p>
          <textarea rows={4} defaultValue={draft.draft_text} readOnly />
          <p>상태: {draft.published ? 'Published' : 'Draft'}</p>
          <button className="primary" onClick={() => togglePublish(draft)}>상태 토글</button>{' '}
          <button className="warn" onClick={() => remove(draft.id)}>삭제</button>
        </article>
      ))}
    </main>
  );
}
