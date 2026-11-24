from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.course import Course
from app.models.enrollment import Enrollment


def list_open_courses(db: Session) -> list[Course]:
    stmt = select(Course).where(Course.is_open.is_(True)).order_by(Course.id)
    return list(db.scalars(stmt))


def get_course(db: Session, course_id: int) -> Course:
    course = db.get(Course, course_id)
    if course is None:
        raise NotFoundError("과정을 찾을 수 없습니다.")
    return course


def count_active_enrollments(db: Session, course_id: int) -> int:
    """취소되지 않은 신청 수. 정원 계산에 사용합니다."""
    stmt = select(func.count()).select_from(Enrollment).where(
        Enrollment.course_id == course_id,
        Enrollment.status != "cancelled",
    )
    return db.scalar(stmt) or 0
