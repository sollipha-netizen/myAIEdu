import hmac
from typing import Optional

from fastapi import Header

from app.core.config import ADMIN_KEY
from app.core.errors import AuthError, ServiceUnavailableError


def require_admin(x_admin_key: Optional[str] = Header(default=None)) -> None:
    """관리자 전용 엔드포인트에 거는 의존성. 헤더 X-Admin-Key 값을 확인합니다."""
    if not ADMIN_KEY:
        raise ServiceUnavailableError("관리자 키가 서버에 설정되지 않았습니다.")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, ADMIN_KEY):
        raise AuthError("관리자 인증에 실패했습니다.")
