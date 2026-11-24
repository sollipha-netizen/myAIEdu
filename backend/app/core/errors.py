class AppError(Exception):
    """서비스 계층에서 던지는 기본 오류. 응답 본문은 {"detail": 메시지}가 됩니다."""

    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class AuthError(AppError):
    status_code = 401


class ServiceUnavailableError(AppError):
    status_code = 503


class PracticeModeError(AppError):
    """실습 모드에서 저장이 필요한 작업을 요청했을 때 쓰는 오류."""

    status_code = 403
