from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import config
from app.core.errors import ConflictError, NotFoundError
from app.models.student import Student
from app.schemas.student import StudentCreate


def create_student(db: Session, data: StudentCreate) -> Student:
    duplicate = db.scalar(select(Student).where(Student.phone == data.phone))
    if duplicate is not None:
        raise ConflictError("이미 등록된 전화번호입니다. 문의해 주세요.")

    now = datetime.now()
    if config.PRACTICE_MODE:
        # 실습 모드: 검증과 중복 검사만 하고 저장하지 않습니다.
        # 응답 형식을 맞추기 위해 id가 0인 임시 객체를 돌려줍니다 (세션에 추가하지 않음).
        return Student(
            id=0,
            name=data.name,
            phone=data.phone,
            email=data.email,
            age_group=data.age_group,
            consented_at=now,
            created_at=now,
        )

    student = Student(
        name=data.name,
        phone=data.phone,
        email=data.email,
        age_group=data.age_group,
        consented_at=now,
        created_at=now,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def list_students(db: Session) -> list[Student]:
    return list(db.scalars(select(Student).order_by(Student.id)))


def get_student(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError("수강생을 찾을 수 없습니다.")
    return student
