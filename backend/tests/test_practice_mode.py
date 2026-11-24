from app.core import config

ADMIN_HEADERS = {"X-Admin-Key": "test-admin-key"}

# 실습 모드 테스트: 신청은 검증만 하고 저장하지 않아야 합니다.
# 실습 모드는 config.PRACTICE_MODE를 바꿔서 켜고, 테스트가 끝나면 monkeypatch가 원래대로 되돌립니다.

STUDENT = {"name": "연습생", "phone": "010-1234-5678", "consent": True, "age_group": "40s"}


def _enable_practice(monkeypatch):
    monkeypatch.setattr(config, "PRACTICE_MODE", True)


def test_health_reports_practice_mode(client, monkeypatch):
    _enable_practice(monkeypatch)
    body = client.get("/health").json()
    assert body == {"status": "ok", "practice_mode": True}


def test_health_reports_normal_mode_by_default(client, monkeypatch):
    monkeypatch.setattr(config, "PRACTICE_MODE", False)
    body = client.get("/health").json()
    assert body["practice_mode"] is False


def test_student_is_validated_but_not_saved(client, monkeypatch):
    _enable_practice(monkeypatch)

    # 형식이 맞는 요청은 201로 받아들여지지만
    response = client.post("/students", json=STUDENT)
    assert response.status_code == 201
    assert response.json()["id"] == 0

    # 관리자 목록에는 아무것도 남지 않아야 합니다
    students = client.get("/students", headers=ADMIN_HEADERS).json()
    assert students == []


def test_invalid_student_is_still_rejected_in_practice_mode(client, monkeypatch):
    _enable_practice(monkeypatch)
    response = client.post("/students", json={**STUDENT, "phone": "12345"})
    assert response.status_code == 422
    assert "휴대폰 번호" in response.json()["detail"]


def test_enrollment_is_checked_but_not_saved(client, monkeypatch):
    _enable_practice(monkeypatch)

    response = client.post("/enrollments", json={"student_id": 0, "course_id": 1})
    assert response.status_code == 201

    # 정원 집계에 잡히지 않아야 합니다 (잔여 좌석이 그대로)
    detail = client.get("/courses/1").json()
    assert detail["enrolled_count"] == 0
    assert detail["seats_left"] == 2


def test_admin_status_change_is_blocked_in_practice_mode(client, monkeypatch):
    _enable_practice(monkeypatch)
    response = client.patch(
        "/enrollments/1",
        json={"status": "paid", "paid_amount": 100000},
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 403
    assert "실습 모드" in response.json()["detail"]
