"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Soccer Club": {
            "description": "Practice soccer skills and play friendly matches",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Track and Field": {
            "description": "Train for sprints, distance, and field events",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops and stage productions",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["zoe@mergington.edu", "isaac@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["harper@mergington.edu", "ethan@mergington.edu"]
        },
        "Math Circle": {
            "description": "Solve challenging problems and explore advanced topics",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["elijah@mergington.edu", "lily@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions with hands-on experiments",
            "schedule": "Fridays, 2:30 PM - 4:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "chloe@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)
