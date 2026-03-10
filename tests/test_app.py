"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivities:
    """Test cases for activities endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

        # Check that we have some expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data

        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        activity_name = "Chess Club"
        email = "test@student.edu"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the student was added to participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        activity_name = "Nonexistent Activity"
        email = "test@student.edu"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self, client):
        """Test signup with an email that's already signed up"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # This email is already in the initial data

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "Student already signed up for this activity" in data["detail"]

    def test_signup_with_new_email(self, client):
        """Test signup with a new email for an activity"""
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

        # Verify the student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestRoot:
    """Test cases for root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"