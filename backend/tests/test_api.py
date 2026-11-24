from tests.conftest import ADMIN_HEADERS


def make_student(client, phone="010-1234-5678", name="홍길동"):
    return client.post("/students", json={"name": name, "phone": phone, "consent": True})


# ---- 과정·커리큘럼 ----

def test_list_courses_returns_open_course(client):
    res = client.get("/courses")
    assert res.status_code == 200
    assert [c["id"] for c in res.json()] == [1]


def test_course_detail_shows_seats(client):
    res = client.get("/courses/1")
    assert res.status_code == 200
    assert res.json()["seats_left"] == 2


def test_curriculum_has_8_weeks(client):
    res = client.get("/courses/1/curriculum")
    assert res.status_code == 200
    weeks = res.json()["weeks"]
    assert [w["week_no"] for w in weeks] == list(range(1, 9))


def test_unknown_course_returns_404(client):
    res = client.get("/courses/999/curriculum")
    assert res.status_code == 404
    assert "detail" in res.json()


# ---- 수강생 등록 ----

def test_create_student_normalizes_phone(client):
    res = make_student(client, phone="010-1234-5678")
    assert res.status_code == 201
    assert res.json()["phone"] == "01012345678"


def test_duplicate_phone_returns_409(client):
    make_student(client)
    res = make_student(client, name="다른사람")
    assert res.status_code == 409


def test_invalid_phone_returns_422_with_korean_message(client):
    res = make_student(client, phone="12345")
    assert res.status_code == 422
    assert "휴대폰" in res.json()["detail"]


def test_consent_required(client):
    res = client.post("/students", json={"name": "홍길동", "phone": "01012345678", "consent": False})
    assert res.status_code == 422
    assert "동의" in res.json()["detail"]


# ---- 신청과 정원 ----

def test_enroll_success(client):
    student_id = make_student(client).json()["id"]
    res = client.post("/enrollments", json={"student_id": student_id, "course_id": 1})
    assert res.status_code == 201
    assert res.json()["status"] == "applied"


def test_duplicate_enrollment_returns_409(client):
    student_id = make_student(client).json()["id"]
    client.post("/enrollments", json={"student_id": student_id, "course_id": 1})
    res = client.post("/enrollments", json={"student_id": student_id, "course_id": 1})
    assert res.status_code == 409


def test_capacity_full_returns_409(client):
    for i in range(2):
        sid = make_student(client, phone=f"0101234567{i}", name=f"수강생{i}").json()["id"]
        assert client.post("/enrollments", json={"student_id": sid, "course_id": 1}).status_code == 201

    sid = make_student(client, phone="01099998888", name="대기자").json()["id"]
    res = client.post("/enrollments", json={"student_id": sid, "course_id": 1})
    assert res.status_code == 409
    assert "정원" in res.json()["detail"]


def test_cancelled_enrollment_frees_seat(client):
    sids = [make_student(client, phone=f"0101234567{i}", name=f"수강생{i}").json()["id"] for i in range(3)]
    first = client.post("/enrollments", json={"student_id": sids[0], "course_id": 1}).json()
    client.post("/enrollments", json={"student_id": sids[1], "course_id": 1})

    # 첫 번째 신청을 취소하면 자리가 하나 생깁니다
    client.patch(f"/enrollments/{first['id']}", json={"status": "cancelled"}, headers=ADMIN_HEADERS)
    res = client.post("/enrollments", json={"student_id": sids[2], "course_id": 1})
    assert res.status_code == 201


# ---- 관리자 보호 ----

def test_admin_endpoint_requires_key(client):
    assert client.get("/students").status_code == 401
    assert client.get("/students", headers={"X-Admin-Key": "wrong"}).status_code == 401
    assert client.get("/students", headers=ADMIN_HEADERS).status_code == 200


def test_admin_can_update_payment(client):
    sid = make_student(client).json()["id"]
    eid = client.post("/enrollments", json={"student_id": sid, "course_id": 1}).json()["id"]
    res = client.patch(
        f"/enrollments/{eid}",
        json={"status": "paid", "paid_amount": 150000},
        headers=ADMIN_HEADERS,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "paid"
    assert res.json()["paid_amount"] == 150000
