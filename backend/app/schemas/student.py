import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

AgeGroup = Literal["40s", "50s", "other"]
PHONE_PATTERN = re.compile(r"01[016789]\d{7,8}")


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str = Field(max_length=30)  # 길이·형식 검사는 아래 validator에서 한글 메시지로 처리
    email: Optional[str] = Field(default=None, max_length=120)
    age_group: Optional[AgeGroup] = None
    consent: bool

    @field_validator("name")
    @classmethod
    def _clean_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("이름을 입력해 주세요.")
        return cleaned

    @field_validator("phone")
    @classmethod
    def _normalize_phone(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if not PHONE_PATTERN.fullmatch(digits):
            raise ValueError("휴대폰 번호를 확인해 주세요. (예: 010-1234-5678)")
        return digits

    @field_validator("email")
    @classmethod
    def _clean_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not value.strip():
            return None
        cleaned = value.strip()
        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("이메일 형식이 올바르지 않습니다.")
        return cleaned

    @field_validator("consent")
    @classmethod
    def _require_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("개인정보 수집·이용에 동의해 주세요.")
        return value


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    email: Optional[str] = None
    age_group: Optional[str] = None
    created_at: datetime
