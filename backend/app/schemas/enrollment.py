from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EnrollmentStatus = Literal["applied", "paid", "cancelled", "completed"]


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentStatusUpdate(BaseModel):
    status: EnrollmentStatus
    paid_amount: Optional[int] = Field(default=None, ge=0)


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    status: str
    paid_amount: int
    enrolled_at: datetime
