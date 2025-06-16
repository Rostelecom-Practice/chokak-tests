import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts"
BASE_URL = os.getenv("API_BASE_URL")

@pytest.fixture(scope="session")
def firebase_test_id_token():
    email = os.getenv("FIREBASE_TEST_EMAIL")
    password = os.getenv("FIREBASE_TEST_PASSWORD")

    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={API_KEY}"
    resp = requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    resp.raise_for_status()
    return resp.json()["idToken"]

@pytest.fixture(scope="session")
def firebase_test_uid(firebase_test_id_token):
    url = f"{FIREBASE_AUTH_URL}:lookup?key={API_KEY}"
    resp = requests.post(url, json={"idToken": firebase_test_id_token})
    resp.raise_for_status()
    users = resp.json().get("users", [])
    assert users, "No users returned from Firebase"
    return users[0]["localId"]
