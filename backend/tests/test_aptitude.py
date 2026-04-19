import pytest


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "username": "aptitudeuser",
        "email": "aptitude@example.com",
        "password": "pass123"
    })
    response = client.post("/api/auth/login", json={
        "username": "aptitudeuser",
        "password": "pass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_question(client, auth_headers):
    response = client.post("/api/aptitude/questions", json={
        "question_type": "判断推理",
        "question_text": "以下哪项最能加强论点？",
        "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
        "correct_answer": "C",
        "difficulty": 3
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["question_type"] == "判断推理"
    assert data["correct_answer"] == "C"
    assert "id" in data


def test_list_questions(client, auth_headers):
    client.post("/api/aptitude/questions", json={
        "question_type": "言语理解",
        "question_text": "填入最恰当的词语",
        "correct_answer": "A"
    }, headers=auth_headers)
    response = client.get("/api/aptitude/questions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_create_attempt(client, auth_headers):
    q_resp = client.post("/api/aptitude/questions", json={
        "question_type": "资料分析",
        "question_text": "根据图表计算增长率",
        "correct_answer": "B"
    }, headers=auth_headers)
    q_id = q_resp.json()["id"]

    response = client.post("/api/aptitude/attempts", json={
        "question_id": q_id,
        "user_answer": "B",
        "time_spent_seconds": 120
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == True
    assert data["is_mistake"] == False


def test_create_attempt_wrong_answer(client, auth_headers):
    q_resp = client.post("/api/aptitude/questions", json={
        "question_type": "数量关系",
        "question_text": "计算甲乙两人相遇时间",
        "correct_answer": "A"
    }, headers=auth_headers)
    q_id = q_resp.json()["id"]

    response = client.post("/api/aptitude/attempts", json={
        "question_id": q_id,
        "user_answer": "C",
        "time_spent_seconds": 180
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == False
    assert data["is_mistake"] == True


def test_get_question(client, auth_headers):
    q_resp = client.post("/api/aptitude/questions", json={
        "question_type": "常识判断",
        "question_text": "下列关于公文格式的说法正确的是？",
        "correct_answer": "D"
    }, headers=auth_headers)
    q_id = q_resp.json()["id"]

    response = client.get(f"/api/aptitude/questions/{q_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["question_type"] == "常识判断"


def test_delete_question(client, auth_headers):
    q_resp = client.post("/api/aptitude/questions", json={
        "question_type": "政治理论",
        "question_text": "新时代中国特色社会主义思想的核心是？",
        "correct_answer": "B"
    }, headers=auth_headers)
    q_id = q_resp.json()["id"]

    response = client.delete(f"/api/aptitude/questions/{q_id}", headers=auth_headers)
    assert response.status_code == 200

    get_resp = client.get(f"/api/aptitude/questions/{q_id}", headers=auth_headers)
    assert get_resp.status_code == 404
