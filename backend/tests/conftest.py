import os

# 앱을 import하기 전에 테스트용 환경 변수를 설정합니다 (실제 app.db를 건드리지 않음)
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["ADMIN_KEY"] = "test-admin-key"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.course import Course, Week  # noqa: E402

ADMIN_HEADERS = {"X-Admin-Key": "test-admin-key"}


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    # 정원 2명짜리 과정 1개 (8주 커리큘럼 포함)
    with TestingSession() as db:
        db.add(Course(
            id=1,
            title="테스트 과정",
            capacity=2,
            is_open=True,
            weeks=[Week(week_no=n, title=f"{n}주차", goal="목표") for n in range(1, 9)],
        ))
        db.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # lifespan(init_db)은 실행하지 않음
    app.dependency_overrides.clear()
