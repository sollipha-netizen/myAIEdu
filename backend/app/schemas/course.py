from typing import Optional

from pydantic import BaseModel, ConfigDict


class WeekOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    week_no: int
    title: str
    goal: Optional[str] = None
    practice_title: Optional[str] = None
    practice_steps: Optional[list[str]] = None


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    price: Optional[int] = None
    capacity: int
    is_open: bool


class CourseDetailOut(CourseOut):
    enrolled_count: int
    seats_left: int


class CurriculumOut(BaseModel):
    course_id: int
    course_title: str
    weeks: list[WeekOut]
