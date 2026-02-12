# 최소 비용 MVP 자동화 시스템

비개발자 기준으로 **바로 실행 가능한 형태**로 만든 자동화 스타터입니다.

## 1) 포함 기능
- YouTube 자동 수집: 최신 영상, 통계, 자막(가능 시), 재시도 로직.
- 뉴스 자동 수집: RSS + Discord 메시지.
- 자동 요약/초안 생성: Short/Standard/Long 기반 요약 + Draft 테이블 저장.
- 대시보드: Home / YouTube / News / Drafts / Settings.
- Supabase 무료 플랜 + Vercel 무료 배포 기준 구성.

## 2) 프로젝트 구조 (파일별 목적 주석)
```txt
/backend                # 수집 서버(API + 스케줄러 + 요약/초안 생성)
  /src
    /collectors         # 통합 수집 실행기(runCollectors)
    /jobs               # 수동 실행 엔트리
    /routes             # REST API 라우터
    /services           # YouTube/RSS/Discord/Supabase 서비스
    /utils              # 재시도/텍스트 처리 유틸
  /test                 # 최소 단위 테스트
/frontend               # Next.js 대시보드
  /app                  # 페이지 라우팅
  /components           # 공통 컴포넌트
/bots                   # Discord/Telegram 봇 예제
/db
  /migrations           # Supabase SQL 마이그레이션
  seed.sql              # 초기 샘플 데이터
/env/.env.example       # 환경변수 샘플
/vercel.json            # Vercel 배포 설정
```

## 3) 빠른 시작
### 3-1. 의존성 설치
```bash
cd backend && npm install
cd ../frontend && npm install
cd ../bots && npm install
```

### 3-2. 환경변수 세팅
```bash
cp env/.env.example env/.env
```
`env/.env`에 실제 키 입력:
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `YOUTUBE_API_KEY`, `YOUTUBE_CHANNEL_IDS`
- `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_IDS`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### 3-3. Supabase 테이블 생성
Supabase SQL Editor에 아래 순서 실행:
1. `db/migrations/001_init.sql`
2. `db/seed.sql` (선택)

## 4) 실행 방법
### 백엔드
```bash
cd backend
npm run dev
```
- 수동 수집: `npm run collect`
- 기본 API: `http://localhost:4000/api/health`

### 프론트엔드
```bash
cd frontend
npm run dev
```
- 대시보드: `http://localhost:3000`

### 봇
```bash
cd bots
npm run discord
npm run telegram
```

## 5) API 요약
- `POST /api/collect/run`: YouTube/RSS/Discord 수집 + 요약 + draft 생성
- `GET /api/videos`: 영상 목록
- `GET /api/news`: 뉴스 목록
- `GET /api/drafts`: 초안 목록
- `PATCH /api/drafts/:id`: 초안 수정/발행 상태 변경
- `DELETE /api/drafts/:id`: 초안 삭제

## 6) 무료 배포 가이드 (Vercel + Supabase)
1. GitHub에 push.
2. Vercel에서 repo import.
3. Root를 `/frontend`로 지정.
4. 환경변수(`NEXT_PUBLIC_API_BASE`) 등록.
5. 백엔드는 Render/Railway/Fly 무료 플랜 중 1개 선택 후 `backend` 배포.
6. `vercel.json` rewrites의 `YOUR_BACKEND_URL` 변경.

## 7) 키 발급 가이드
### YouTube API Key
- Google Cloud Console > API & Services > Credentials > API Key.
- YouTube Data API v3 활성화.

### Discord Bot
- Discord Developer Portal > New Application > Bot 생성.
- Privileged Gateway Intent(Message Content) 활성화.
- OAuth2 URL Generator로 서버 초대.
- 채널 ID는 Discord 개발자 모드에서 복사.

### Telegram Bot
- Telegram `@BotFather` > `/newbot`.
- 받은 토큰을 `TELEGRAM_BOT_TOKEN`에 저장.
- `@userinfobot` 혹은 getUpdates로 chat id 확인.

## 8) 운영 팁
- Rate limit: YouTube는 API quota를 아끼기 위해 `AUTO_COLLECT_MINUTES=30~60` 권장.
- Failover: 외부 API 실패 시 수집기는 빈 결과로 넘어가도록 설계되어 전체 중단을 줄임.
- 초안 톤/길이 옵션은 `backend/src/utils/text.js`에서 조정 가능.

## 9) 검증 체크리스트
- [ ] `/api/collect/run` 호출 시 DB에 videos/news/drafts 적재
- [ ] 대시보드 목록 로딩
- [ ] Drafts 페이지에서 상태 토글/삭제 동작
- [ ] 봇 접속 및 ping/start 응답

## 10) 스크린샷 가이드
아래 명령으로 실행 후 화면 캡처:
```bash
cd backend && npm run dev
cd frontend && npm run dev
```
브라우저에서 `http://localhost:3000` 접속 후 Home/YouTube/News/Drafts 확인.
