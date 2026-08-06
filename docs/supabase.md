# Supabase 랭킹 기능 정리

게임 오버 → 닉네임 입력 → DB 저장 → TOP 10 랭킹 표시.
학습용이라 보안 설정은 최소한만 합니다.

---

## 1. Supabase 설정

### 1-1. 프로젝트 만들기

1. https://supabase.com 가입 → **New project**
2. 이름 / DB 비밀번호 / 리전(Northeast Asia - Seoul 추천) 입력 후 생성 (1~2분 소요)

### 1-2. 테이블 만들기

왼쪽 메뉴 **SQL Editor** → 아래 SQL 붙여넣고 **Run**

```sql
-- 점수 테이블
create table scores (
  id         bigint generated always as identity primary key,
  nickname   text not null,
  score      int  not null,
  created_at timestamptz default now()
);

-- RLS(Row Level Security)를 켜면 기본적으로 아무도 접근 못 함.
-- 학습용이므로 "누구나 읽기/쓰기 가능" 정책을 추가한다.
alter table scores enable row level security;

create policy "anyone can select" on scores
  for select to anon using (true);

create policy "anyone can insert" on scores
  for insert to anon with check (true);
```

> ⚠️ 이 정책은 **아무나 점수를 넣을 수 있다**는 뜻입니다. 학습용에서만 쓰세요.
> (Table Editor에서 RLS 자체를 꺼도 동작하지만, 정책을 쓰는 쪽이 정석입니다.)

### 1-3. 필요한 정보 2개 복사

**Project Settings(톱니바퀴) → API** 메뉴에서:

| 이름 | 생김새 | 용도 |
|---|---|---|
| **Project URL** | `https://abcdefgh.supabase.co` | 접속 주소 |
| **anon public key** | `eyJhbGci...` (긴 문자열) | 클라이언트용 공개 키 |

- `anon` 키는 브라우저/앱에 노출되는 걸 전제로 만든 키라 이 정도 프로젝트에는 충분합니다.
- `service_role` 키는 **모든 권한**을 가진 키입니다. 절대 코드나 깃허브에 넣지 마세요.

---

## 2. 로컬 설정

### 2-1. 패키지 설치

```bash
pip install -r requirements.txt
```

(`pygame`, `supabase`, `python-dotenv`)

### 2-2. `.env` 파일 만들기

프로젝트 루트에 `.env` 파일을 만들고 1-3에서 복사한 값을 넣습니다.
(`.env.example`을 복사해서 쓰면 편합니다.)

```
SUPABASE_URL=https://abcdefgh.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
```

`.env`는 `.gitignore`에 등록되어 있어 깃에 올라가지 않습니다.

> `.env`가 없어도 게임은 그대로 돌아갑니다. 저장/조회만 건너뛰고 랭킹 화면이 `(no data)`로 뜹니다.

---

## 3. 코드에서 어떻게 붙였나

### 파일 구성

| 파일 | 역할 |
|---|---|
| `leaderboard.py` | **(신규)** Supabase 저장/조회 함수 2개 |
| `main.py` | 상태 흐름에 `NAME`(닉네임 입력) / `RANK`(랭킹) 추가 |
| `renderer.py` | 닉네임 입력 화면, 랭킹 화면 그리기 추가 |

### 3-1. `leaderboard.py` — DB 통신

```python
from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# INSERT: insert into scores (nickname, score) values (...)
client.table("scores").insert({"nickname": nickname, "score": score}).execute()

# SELECT: select nickname, score from scores order by score desc limit 10
client.table("scores").select("nickname, score").order("score", desc=True).limit(10).execute()
```

- 조회 결과는 `response.data`에 `[{"nickname": "abc", "score": 12}, ...]` 형태로 들어옵니다.
- 네트워크 오류로 게임이 죽지 않도록 `try/except`로 감싸고, 실패하면 `False` / 빈 리스트를 돌려줍니다.

### 3-2. `main.py` — 게임 상태 흐름

```
PLAY ──(충돌)──▶ NAME ──(Enter: 저장)──▶ RANK ──(Space)──▶ PLAY
                    └──(Esc: 저장 안 함)──▶ RANK
```

닉네임은 `pygame.KEYDOWN`의 `event.unicode`를 한 글자씩 이어 붙여서 받습니다.
Backspace는 마지막 글자 삭제, 최대 12글자입니다.

### 3-3. 알아두면 좋은 점

- **네트워크 요청 동안 화면이 잠깐 멈춥니다.** Enter를 누른 순간 저장+조회가 순서대로 일어나기 때문인데, 게임이 이미 끝난 시점이라 실사용에는 문제가 없습니다.
- 한글 닉네임은 폰트(맑은 고딕 등)가 있으면 보이지만, pygame은 한글 IME 조합 입력을 제대로 못 받습니다. **영문 닉네임을 권장**합니다.

---

## 4. 커밋 전 체크리스트

- [ ] `.gitignore`에 `.env` 있는지 확인
- [ ] 코드에 키를 직접 써넣지 않았는지 확인 (`os.getenv`로만 읽기)
- [ ] `.env.example`에는 **가짜 값**만 넣기
- [ ] 실수로 키를 커밋했다면 → Supabase **Settings → API → Reset/Rotate**로 키 재발급
  (커밋을 지워도 깃 히스토리에 남기 때문에 반드시 재발급해야 합니다)
