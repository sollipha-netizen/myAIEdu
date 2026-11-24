from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut, EnrollmentStatusUpdate
from app.services import enrollment_service

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("", response_model=EnrollmentOut, status_code=201, summary="과정 신청 (정원·중복 검사)")
def create_enrollment(data: EnrollmentCreate, db: Session = Depends(get_db)):
    return enrollment_service.enroll(db, data)


@router.patch("/{enrollment_id}", response_model=EnrollmentOut, dependencies=[Depends(require_admin)], summary="신청 상태 변경 (관리자)")
def update_enrollment(enrollment_id: int, data: EnrollmentStatusUpdate, db: Session = Depends(get_db)):
    return enrollment_service.update_enrollment(db, enrollment_id, data)
