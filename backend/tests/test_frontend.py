def test_root_serves_the_frontend_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "수강 신청" in response.text


def test_api_routes_still_return_json_next_to_the_frontend(client):
    # 정적 파일 마운트가 API 경로를 가로채지 않아야 합니다
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert client.get("/health").json()["status"] == "ok"


def test_script_is_served_from_the_same_origin(client):
    response = client.get("/js/app.js")
    assert response.status_code == 200
    assert "API_BASE" in response.text
