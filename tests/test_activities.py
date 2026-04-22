"""Tests for GET /activities endpoint"""
import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities_data = response.json()
    
    # Verify all expected activities are present
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
    ]
    for activity_name in expected_activities:
        assert activity_name in activities_data


def test_get_activities_returns_valid_structure(client):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities_data = response.json()
    
    # Check structure of a sample activity
    chess_club = activities_data["Chess Club"]
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    for field in required_fields:
        assert field in chess_club, f"Activity missing required field: {field}"


def test_get_activities_participants_is_list(client):
    """Test that participants field is a list"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities_data = response.json()
    
    for activity_name, activity_data in activities_data.items():
        assert isinstance(activity_data["participants"], list), \
            f"{activity_name} participants should be a list"


def test_get_activities_contains_initial_participants(client):
    """Test that activities contain initial participants"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities_data = response.json()
    
    # Chess Club should have initial participants
    chess_club = activities_data["Chess Club"]
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_get_activities_max_participants_is_integer(client):
    """Test that max_participants is an integer"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities_data = response.json()
    
    for activity_name, activity_data in activities_data.items():
        assert isinstance(activity_data["max_participants"], int), \
            f"{activity_name} max_participants should be an integer"
        assert activity_data["max_participants"] > 0


def test_get_activities_returns_correct_participant_count(client):
    """Test that participant counts are accurate"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities_data = response.json()
    
    # Programming Class should have 2 participants initially
    programming = activities_data["Programming Class"]
    assert len(programming["participants"]) == 2
    assert "emma@mergington.edu" in programming["participants"]
    assert "sophia@mergington.edu" in programming["participants"]
