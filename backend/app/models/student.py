from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20), unique=True)  # 중복 가입 방지 키 (숫자만 저장)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    age_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    memo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consented_at: Mapped[datetime] = mapped_column(DateTime)  # 개인정보 수집 동의 시각
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
