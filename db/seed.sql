insert into videos (youtube_id, title, caption, views, likes, comments, summary_short, summary_long)
values ('demo001', '샘플 영상', '샘플 자막', 100, 10, 5, '짧은 요약', '긴 요약')
on conflict (youtube_id) do nothing;

insert into news (source, title, raw_text, summary_short, summary_long)
values ('rss:demo', '샘플 뉴스', '샘플 뉴스 본문', '짧은 뉴스 요약', '긴 뉴스 요약');

insert into drafts (source_type, draft_text, published)
values ('news', '[NEWS] 샘플 초안', false);
