-- DemoBoard 스키마: posts, comments 테이블
-- Supabase 대시보드 > SQL Editor에서 한 번 실행하세요.

create table if not exists posts (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  author text not null,
  content text not null,
  views integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references posts (id) on delete cascade,
  author text not null,
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists comments_post_id_idx on comments (post_id);

-- 조회수를 원자적으로 1 증가시키는 함수 (동시 조회 시 read-then-write 경쟁 방지)
create or replace function increment_post_views(post_id uuid)
returns void
language sql
as $$
  update posts set views = views + 1 where id = post_id;
$$;

-- 데모 앱이라 인증 없이 publishable(anon) key로 바로 읽고 쓸 수 있도록
-- RLS를 켜고 전체 허용 정책을 추가합니다.
-- 실제 서비스라면 사용자 인증에 맞춰 정책을 좁혀야 합니다.
alter table posts enable row level security;
alter table comments enable row level security;

drop policy if exists "public posts access" on posts;
create policy "public posts access" on posts
  for all
  using (true)
  with check (true);

drop policy if exists "public comments access" on comments;
create policy "public comments access" on comments
  for all
  using (true)
  with check (true);

-- RLS 정책과 별개로 테이블 자체에 대한 권한도 있어야 anon/authenticated 역할이 접근 가능합니다.
grant usage on schema public to anon, authenticated;
grant select, insert, update, delete on posts, comments to anon, authenticated;
grant execute on function increment_post_views(uuid) to anon, authenticated;

-- 기존 data/db.json에 있던 시드 데이터
insert into posts (id, title, author, content, views, created_at, updated_at)
values
  (
    '11111111-1111-1111-1111-111111111111',
    'DemoBoard에 오신 것을 환영합니다',
    '관리자',
    E'이곳은 Next.js와 shadcn/ui로 만든 데모 게시판입니다.\n글쓰기, 수정, 삭제, 댓글 기능을 자유롭게 사용해 보세요.',
    12,
    '2026-09-20T09:00:00.000Z',
    '2026-09-20T09:00:00.000Z'
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'shadcn/ui 컴포넌트 사용 팁',
    '개발자',
    'Button, Card, Table, Dialog 등 다양한 컴포넌트를 조합해서 게시판 UI를 구성했습니다.',
    5,
    '2026-09-21T03:30:00.000Z',
    '2026-09-21T03:30:00.000Z'
  )
on conflict (id) do nothing;

insert into comments (id, post_id, author, content, created_at)
values
  (
    '33333333-3333-3333-3333-333333333333',
    '11111111-1111-1111-1111-111111111111',
    '방문자',
    '잘 보고 갑니다!',
    '2026-09-21T05:00:00.000Z'
  )
on conflict (id) do nothing;
