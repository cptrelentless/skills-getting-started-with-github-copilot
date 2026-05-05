"""Backend integration tests for the Mergington High School API."""


def test_root_redirects_to_static(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert isinstance(chess_club["participants"], list)
    assert "michael@mergington.edu" in chess_club["participants"]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]

    verify = client.get("/activities").json()
    assert "newstudent@mergington.edu" in verify["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity_returns_404(client):
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"

    verify = client.get("/activities").json()
    assert "michael@mergington.edu" not in verify["Chess Club"]["participants"]


def test_unregister_nonexistent_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_nonexistent_activity_returns_404(client):
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_then_unregister_workflow(client):
    email = "student.workflow@mergington.edu"
    response = client.post(
        "/activities/Music Band/signup",
        params={"email": email}
    )
    assert response.status_code == 200

    verify = client.get("/activities").json()
    assert email in verify["Music Band"]["participants"]

    response = client.delete(
        "/activities/Music Band/unregister",
        params={"email": email}
    )
    assert response.status_code == 200

    verify = client.get("/activities").json()
    assert email not in verify["Music Band"]["participants"]
