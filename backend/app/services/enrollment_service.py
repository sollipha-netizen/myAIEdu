from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import config
from app.core.errors import ConflictError, NotFoundError, PracticeModeError
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.schemas.enrollment import EnrollmentCreate, EnrollmentStatusUpdate
from app.services.course_service import count_active_enrollments


def enroll(db: Session, data: EnrollmentCreate) -> Enrollment:
    """과정 신청. 중복 신청과 정원 초과를 막습니다.

    실습 모드(PRACTICE_MODE)에서는 같은 규칙으로 검사만 하고 저장하지 않습니다.
    실습 모드에서는 수강생 등록도 저장되지 않으므로 수강생 존재 확인을 건너뜁니다.

    주의: SQLite에서는 동시 신청이 몰리면 정원을 조금 넘을 수 있습니다.
    실서비스에서는 PostgreSQL로 옮기고 행 잠금(with_for_update)을 사용하세요.
    """
    if not config.PRACTICE_MODE:
        student = db.get(Student, data.student_id)
        if student is None:
            raise NotFoundError("수강생 정보를 찾을 수 없습니다. 다시 등록해 주세요.")

    course = db.get(Course, data.course_id)
    if course is None or not course.is_open:
        raise NotFoundError("모집 중인 과정이 아닙니다.")

    existing = db.scalar(
        select(Enrollment).where(
            Enrollment.student_id == data.student_id,
            Enrollment.course_id == data.course_id,
        )
    )
    if existing is not None and existing.status != "cancelled":
        raise ConflictError("이미 신청한 과정입니다.")

    if count_active_enrollments(db, course.id) >= course.capacity:
        raise ConflictError("정원이 모두 찼습니다.")

    now = datetime.now()
    if config.PRACTICE_MODE:
        # 실습 모드: 저장하지 않고 응답용 임시 객체만 돌려줍니다.
        return Enrollment(
            id=0,
            student_id=data.student_id,
            course_id=data.course_id,
            status="applied",
            paid_amount=0,
            enrolled_at=now,
        )

    if existing is not None:
        # 취소했던 신청을 다시 살립니다 (UNIQUE 제약 때문에 새 행을 만들지 않음)
        existing.status = "applied"
        existing.enrolled_at = now
        enrollment = existing
    else:
        enrollment = Enrollment(
            student_id=data.student_id,
            course_id=data.course_id,
            status="applied",
            paid_amount=0,
            enrolled_at=now,
        )
        db.add(enrollment)

    db.commit()
    db.refresh(enrollment)
    return enrollment


def update_enrollment(db: Session, enrollment_id: int, data: EnrollmentStatusUpdate) -> Enrollment:
    if config.PRACTICE_MODE:
        raise PracticeModeError("실습 모드에서는 신청 상태를 바꿀 수 없습니다.")

    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise NotFoundError("신청 내역을 찾을 수 없습니다.")

    enrollment.status = data.status
    if data.paid_amount is not None:
        enrollment.paid_amount = data.paid_amount

    db.commit()
    db.refresh(enrollment)
    return enrollment
