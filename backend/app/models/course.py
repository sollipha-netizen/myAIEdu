from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # None이면 "추후 안내"
    capacity: Mapped[int] = mapped_column(Integer)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    weeks: Mapped[list["Week"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Week.week_no",
    )


class Week(Base):
    __tablename__ = "weeks"
    __table_args__ = (UniqueConstraint("course_id", "week_no", name="uq_week_course_no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    week_no: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    practice_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    practice_steps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    course: Mapped[Course] = relationship(back_populates="weeks")
