import os
from pathlib import Path

# backend/ 폴더 기준 경로 (현재 작업 디렉터리와 무관하게 동작)
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}",
)

# 관리자 API 키. 비어 있으면 관리자 기능이 꺼진 상태로 동작합니다.
ADMIN_KEY = os.getenv("ADMIN_KEY", "")

# 페이지와 API를 같은 주소(백엔드 한 곳)에서 제공하므로 기본적으로 CORS는 필요 없습니다.
# 페이지를 다른 주소에서 따로 열 때만 쉼표로 출처를 적어 주세요.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

# 프론트엔드 정적 파일 폴더 (백엔드가 같은 주소에서 함께 서빙합니다)
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# 실습 모드. "1"이면 수강생 등록과 신청을 검증만 하고 저장하지 않습니다.
# 팀원과 공유하는 서버에서 켭니다. 관리자 상태 변경도 막습니다.
PRACTICE_MODE = os.getenv("PRACTICE_MODE", "0") == "1"
