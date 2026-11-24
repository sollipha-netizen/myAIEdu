from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core import config
from app.core.config import CORS_ORIGINS, FRONTEND_DIR
from app.core.database import init_db
from app.core.errors import AppError
from app.routers import courses, enrollments, students


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()  # 테이블이 없으면 생성
    yield


app = FastAPI(title="4050 AI 교육 API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError):
    # 프론트엔드가 detail을 그대로 보여 주므로 첫 번째 오류 메시지를 한 줄로 돌려줍니다.
    errors = exc.errors()
    detail = "입력값을 확인해 주세요."
    if errors:
        first = errors[0]
        if first.get("type") == "missing":
            detail = f"{first['loc'][-1]} 항목은 필수입니다."
        else:
            detail = str(first.get("msg", detail)).removeprefix("Value error, ")
    return JSONResponse(status_code=422, content={"detail": detail})


app.include_router(courses.router)
app.include_router(students.router)
app.include_router(enrollments.router)


@app.get("/health", tags=["system"], summary="서버 상태 확인")
def health():
    # practice_mode: 프론트가 "저장되지 않는다"는 안내를 보여 줄 때 씁니다.
    return {"status": "ok", "practice_mode": config.PRACTICE_MODE}


# 프론트엔드 화면. API 라우트를 모두 등록한 뒤 마지막에 붙여야 API 경로가 먼저 매칭됩니다.
# html=True: 주소 "/"는 index.html을 돌려줍니다.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
