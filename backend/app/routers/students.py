from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentOut
from app.services import student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentOut, status_code=201, summary="수강생 등록 (개인정보 동의 필수)")
def create_student(data: StudentCreate, db: Session = Depends(get_db)) -> Student:
    return student_service.create_student(db, data)


@router.get("", response_model=list[StudentOut], dependencies=[Depends(require_admin)], summary="수강생 목록 조회 (관리자)")
def list_students(db: Session = Depends(get_db)):
    return student_service.list_students(db)


@router.get("/{student_id}", response_model=StudentOut, dependencies=[Depends(require_admin)], summary="수강생 상세 조회 (관리자)")
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    return student_service.get_student(db, student_id)
