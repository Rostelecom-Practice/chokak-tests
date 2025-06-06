import requests
import os
import pytest
from dotenv import load_dotenv


load_dotenv()

@pytest.fixture(scope="session")
def firebase_test_id_token():
    api_key = os.getenv("FIREBASE_API_KEY")
    email = os.getenv("FIREBASE_TEST_EMAIL")
    password = os.getenv("FIREBASE_TEST_PASSWORD")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    id_token = response.json()["idToken"]
    return id_token