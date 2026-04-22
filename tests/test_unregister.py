"""Tests for DELETE /activities/{activity_name}/unregister endpoint"""
import pytest


def test_unregister_successful(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert "michael@mergington.edu" in response.json()["message"]


def test_unregister_removes_participant_from_activity(client):
    """Test that unregister removes the participant from the activity"""
    # Verify participant is initially signed up
    before = client.get("/activities").json()
    assert "michael@mergington.edu" in before["Chess Club"]["participants"]
    
    # Unregister
    client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    # Verify participant was removed
    after = client.get("/activities").json()
    assert "michael@mergington.edu" not in after["Chess Club"]["participants"]


def test_unregister_nonexistent_activity_fails(client):
    """Test that unregister from non-existent activity fails"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_not_registered_student_fails(client):
    """Test that unregistering a student not in the activity fails"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_twice_fails(client):
    """Test that unregistering twice fails"""
    email = "michael@mergington.edu"
    
    # First unregister should succeed
    response1 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "not signed up" in response2.json()["detail"].lower()


def test_unregister_decrements_participant_count(client):
    """Test that unregister decrements the participant count"""
    # Get initial count
    before = client.get("/activities").json()
    initial_count = len(before["Chess Club"]["participants"])
    
    # Unregister a participant
    client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    # Get updated count
    after = client.get("/activities").json()
    new_count = len(after["Chess Club"]["participants"])
    
    assert new_count == initial_count - 1


def test_unregister_returns_correct_message_format(client):
    """Test that unregister returns a properly formatted message"""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"


def test_unregister_preserves_other_participants(client):
    """Test that unregistering one participant doesn't affect others"""
    activity = "Chess Club"
    
    # Get initial participants
    before = client.get("/activities").json()
    initial_participants = before[activity]["participants"].copy()
    
    # Unregister Michael
    client.delete(
        f"/activities/{activity}/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    # Get updated participants
    after = client.get("/activities").json()
    updated_participants = after[activity]["participants"]
    
    # Verify Daniel is still there
    assert "daniel@mergington.edu" in updated_participants
    
    # Verify only Michael was removed
    assert len(updated_participants) == len(initial_participants) - 1


def test_unregister_then_signup_same_student(client):
    """Test that a student can unregister and sign up again"""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Unregister
    response1 = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Verify unregistered
    check1 = client.get("/activities").json()
    assert email not in check1[activity]["participants"]
    
    # Sign up again
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify re-registered
    check2 = client.get("/activities").json()
    assert email in check2[activity]["participants"]


def test_unregister_preserves_other_activities(client):
    """Test that unregistering from one activity doesn't affect other activities"""
    # Get initial state
    before = client.get("/activities").json()
    programming_before = before["Programming Class"]["participants"].copy()
    
    # Unregister from Chess Club (not Programming Class)
    client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    # Verify other activities unchanged
    after = client.get("/activities").json()
    assert after["Programming Class"]["participants"] == programming_before


def test_unregister_multiple_participants_same_activity(client):
    """Test unregistering multiple participants from the same activity"""
    activity = "Chess Club"
    participants_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
    
    for email in participants_to_remove:
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all removed
    after = client.get("/activities").json()
    for email in participants_to_remove:
        assert email not in after[activity]["participants"]
    
    # Verify activity still exists and is empty
    assert activity in after
    assert len(after[activity]["participants"]) == 0
