"""Tests for POST /activities/{activity_name}/signup endpoint"""
import pytest


def test_signup_successful(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert "newstudent@mergington.edu" in response.json()["message"]


def test_signup_adds_participant_to_activity(client):
    """Test that signup adds the participant to the activity"""
    # Sign up a new student
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "alice@mergington.edu"}
    )
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "alice@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_student_fails(client):
    """Test that signing up the same student twice fails"""
    # First signup should succeed
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": "bob@mergington.edu"}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": "bob@mergington.edu"}
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_already_registered_student_fails(client):
    """Test that signing up an already registered student fails"""
    # Try to sign up Michael who is already in Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity_fails(client):
    """Test that signup for non-existent activity fails"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_multiple_students_same_activity(client):
    """Test that multiple different students can sign up for the same activity"""
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
    
    for email in emails:
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all students are signed up
    activities = client.get("/activities").json()
    for email in emails:
        assert email in activities["Art Club"]["participants"]


def test_signup_same_student_different_activities(client):
    """Test that the same student can sign up for multiple activities"""
    email = "versatile@mergington.edu"
    activities_to_join = ["Chess Club", "Art Club", "Science Club"]
    
    for activity in activities_to_join:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify student is in all activities
    activities_data = client.get("/activities").json()
    for activity in activities_to_join:
        assert email in activities_data[activity]["participants"]


def test_signup_increments_participant_count(client):
    """Test that signup increments the participant count"""
    # Get initial count
    before = client.get("/activities").json()
    initial_count = len(before["Basketball Team"]["participants"])
    
    # Sign up a new student
    client.post(
        "/activities/Basketball Team/signup",
        params={"email": "newplayer@mergington.edu"}
    )
    
    # Get updated count
    after = client.get("/activities").json()
    new_count = len(after["Basketball Team"]["participants"])
    
    assert new_count == initial_count + 1


def test_signup_returns_correct_message_format(client):
    """Test that signup returns a properly formatted message"""
    email = "testuser@mergington.edu"
    activity = "Drama Club"
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"


def test_signup_with_special_characters_in_activity_name(client):
    """Test signup with URL-encoded activity names"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 200


def test_signup_preserves_other_activity_participants(client):
    """Test that signing up for one activity doesn't affect other activities"""
    # Get initial state
    before = client.get("/activities").json()
    chess_before = before["Chess Club"]["participants"].copy()
    art_before = before["Art Club"]["participants"].copy()
    
    # Sign up for Chess Club
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    # Verify other activity unchanged
    after = client.get("/activities").json()
    assert after["Art Club"]["participants"] == art_before
    
    # Verify Chess Club has one more participant
    assert len(after["Chess Club"]["participants"]) == len(chess_before) + 1
