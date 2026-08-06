# Supabase DB와 통신하는 부분만 모아둔 파일
# 게임 로직(snake_game.py), 화면(renderer.py)과 분리되어 있어서
# 나중에 DB를 다른 걸로 바꿔도 이 파일만 고치면 됨

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# 클라이언트를 매번 새로 만들면 낭비이므로 한 번 만든 걸 재사용(캐싱)
_client = None


def get_client():
    # Supabase 접속 객체를 반환. 키가 없으면 None을 반환해서
    # DB 설정을 안 한 사람도 게임 자체는 그냥 플레이할 수 있게 함
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            return None
        _client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _client


def save_score(nickname, score):
    # scores 테이블에 { nickname, score } 한 줄을 INSERT
    # 반환값: 성공하면 True, 실패하면 False
    client = get_client()
    if client is None:
        print("[leaderboard] .env에 SUPABASE_URL / SUPABASE_ANON_KEY가 없어 저장을 건너뜁니다.")
        return False

    try:
        client.table("scores").insert({"nickname": nickname, "score": score}).execute()
        return True
    except Exception as e:
        # 인터넷이 끊겼거나 테이블 이름이 틀린 경우 등
        # 게임이 죽지 않도록 예외를 잡아서 메시지만 출력
        print("[leaderboard] 저장 실패:", e)
        return False


def get_top10():
    # 점수가 높은 순으로 10개를 SELECT
    # SQL로 치면: select nickname, score from scores order by score desc limit 10
    # 반환값: [{"nickname": "abc", "score": 12}, ...] 형태의 리스트
    client = get_client()
    if client is None:
        return []

    try:
        response = (
            client.table("scores")
            .select("nickname, score")
            .order("score", desc=True)
            .limit(10)
            .execute()
        )
        return response.data
    except Exception as e:
        print("[leaderboard] 조회 실패:", e)
        return []
