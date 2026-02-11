"""Tests for the Mergington High School API endpoints"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # We have 9 activities
        
        # Check that key activities exist
        assert "Soccer Club" in data
        assert "Drama Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Soccer Club structure
        soccer = data["Soccer Club"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)
    
    def test_get_activities_has_correct_initial_participants(self, client):
        """Test that activities have the correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "liam@mergington.edu" in data["Soccer Club"]["participants"]
        assert "ava@mergington.edu" in data["Soccer Club"]["participants"]


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Soccer Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Soccer Club"
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "test@mergington.edu" in activities["Soccer Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client):
        """Test that signing up twice fails"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Soccer Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Soccer Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Drama Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        for email in emails:
            assert email in activities["Drama Club"]["participants"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name (spaces)"""
        response = client.post(
            "/activities/Track%20and%20Field/signup?email=runner@mergington.edu"
        )
        assert response.status_code == 200
        assert "Track and Field" in response.json()["message"]


class TestRemoveParticipantEndpoint:
    """Tests for the remove participant endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successfully removing a participant from an activity"""
        # First, add a participant
        email = "remove@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Then remove them
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from Chess Club"
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_remove_participant_from_nonexistent_activity(self, client):
        """Test removing a participant from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_nonexistent_participant(self, client):
        """Test removing a participant that isn't in the activity"""
        response = client.delete(
            "/activities/Math Circle/participants/notmember@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
    
    def test_remove_initial_participant(self, client):
        """Test removing an initial participant from an activity"""
        # Remove an initial participant
        response = client.delete(
            "/activities/Soccer Club/participants/liam@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify they were removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "liam@mergington.edu" not in activities["Soccer Club"]["participants"]
        # But ava should still be there
        assert "ava@mergington.edu" in activities["Soccer Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_complete_signup_and_removal_workflow(self, client):
        """Test a complete workflow of viewing, signing up, and removing"""
        email = "workflow@mergington.edu"
        activity = "Art Studio"
        
        # 1. View activities
        response = client.get("/activities")
        assert response.status_code == 200
        initial_count = len(response.json()[activity]["participants"])
        
        # 2. Sign up for activity
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # 3. Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        
        # 4. Remove participant
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        # 5. Verify removal
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        assert len(response.json()[activity]["participants"]) == initial_count
    
    def test_multiple_activities_signup(self, client):
        """Test signing up for multiple activities"""
        email = "multisport@mergington.edu"
        activities = ["Soccer Club", "Drama Club", "Programming Class"]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        response = client.get("/activities")
        all_activities = response.json()
        for activity in activities:
            assert email in all_activities[activity]["participants"]
