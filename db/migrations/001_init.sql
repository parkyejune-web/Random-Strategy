-- Enable UUID generation
create extension if not exists "pgcrypto";

create table if not exists videos (
  id uuid primary key default gen_random_uuid(),
  youtube_id text unique,
  title text,
  caption text,
  views integer default 0,
  likes integer default 0,
  comments integer default 0,
  summary_short text,
  summary_long text,
  collected_at timestamp default now()
);

create table if not exists news (
  id uuid primary key default gen_random_uuid(),
  source text,
  title text,
  raw_text text,
  summary_short text,
  summary_long text,
  collected_at timestamp default now()
);

create table if not exists drafts (
  id uuid primary key default gen_random_uuid(),
  source_type text,
  draft_text text,
  created_at timestamp default now(),
  published boolean default false
);

create index if not exists idx_videos_collected_at on videos (collected_at desc);
create index if not exists idx_news_collected_at on news (collected_at desc);
create index if not exists idx_drafts_created_at on drafts (created_at desc);
