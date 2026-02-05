"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_success(self):
        """Test that /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that /activities returns all expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Basketball",
            "Tennis Club",
            "Drama Club",
            "Painting Studio",
            "Debate Team",
            "Science Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_with_valid_email_and_activity(self):
        """Test successful signup"""
        email = "test@mergington.edu"
        activity = "Basketball"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_email_returns_error(self):
        """Test that signing up with duplicate email fails"""
        email = "alex@mergington.edu"
        activity = "Basketball"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for non-existent activity returns 404"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        activity = "Tennis Club"
        
        # Get initial participants count
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity]["participants"].copy()
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get updated participants count
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity]["participants"]
        
        assert email in participants_after
        assert len(participants_after) == len(participants_before) + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_with_valid_email_and_activity(self):
        """Test successful unregister"""
        email = "jordan@mergington.edu"
        activity = "Tennis Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from non-existent activity returns 404"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_non_participant_returns_error(self):
        """Test that unregistering a non-participant fails"""
        email = "notregistered@mergington.edu"
        activity = "Basketball"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister actually removes the participant"""
        email = "avery@mergington.edu"
        activity = "Drama Club"
        
        # Get initial participants count
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity]["participants"].copy()
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Get updated participants count
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity]["participants"]
        
        assert email not in participants_after
        assert len(participants_after) == len(participants_before) - 1


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_endpoint_redirects(self):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
