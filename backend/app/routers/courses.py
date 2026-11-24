from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.course import CourseDetailOut, CourseOut, CurriculumOut, WeekOut
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut], summary="모집 중인 과정 목록 조회")
def list_courses(db: Session = Depends(get_db)):
    return course_service.list_open_courses(db)


@router.get("/{course_id}", response_model=CourseDetailOut, summary="과정 상세 및 잔여 좌석 조회")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = course_service.get_course(db, course_id)
    enrolled = course_service.count_active_enrollments(db, course_id)
    return CourseDetailOut(
        **CourseOut.model_validate(course).model_dump(),
        enrolled_count=enrolled,
        seats_left=max(course.capacity - enrolled, 0),
    )


@router.get("/{course_id}/curriculum", response_model=CurriculumOut, summary="주차별 커리큘럼 조회")
def get_curriculum(course_id: int, db: Session = Depends(get_db)):
    course = course_service.get_course(db, course_id)
    return CurriculumOut(
        course_id=course.id,
        course_title=course.title,
        weeks=[WeekOut.model_validate(week) for week in course.weeks],
    )
