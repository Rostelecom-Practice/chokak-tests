import uuid

import requests
import os


BASE_URL = os.getenv("API_BASE_URL")

def test_get_my_reviews(firebase_test_id_token, firebase_test_uid):
    headers = {
        "Authorization": f"Bearer {firebase_test_id_token}",
        "X-User-Uid": firebase_test_uid
    }

    url = f"{BASE_URL}/api/users/me/reviews"
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list), "Waiting for a list of reviews"
    for review in data:
        assert "id" in review
        assert "rating" in review
        assert "text" in review
        assert review.get("userUid") == firebase_test_uid

def test_get_places_cities():
    url = f"{BASE_URL}/api/places/cities"
    resp = requests.get(url)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list), "Expected a list of cities"
    for city in data:
        assert "id" in city
        assert "name" in city


def test_get_places_categories():
    url = f"{BASE_URL}/api/places/categories"
    resp = requests.get(url)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list), "Expected a list of categories"
    for category in data:
        assert "id" in category
        assert "name" in category

def submit_review(headers: dict) -> tuple[str,str]:
    source_id = str(uuid.uuid4())
    payload = {
        "sourceId": source_id,
        "organizationId": str(uuid.uuid4()),
        "title": "Test Review Title",
        "content": "This is a test review content",
        "rating": {"value": 4},
        "url": "http://example.com"
    }
    resp = requests.post(f"{BASE_URL}/api/review/submit", headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data["reviewId"], source_id

def test_submit_review(firebase_test_id_token, firebase_test_uid):
    headers = {
        "Authorization": f"Bearer {firebase_test_id_token}",
        "X-User-Uid": firebase_test_uid
    }
    review_id = submit_review(headers)
    assert review_id is not None


def test_reply_review(firebase_test_id_token, firebase_test_uid):
    headers = {
        "Authorization": f"Bearer {firebase_test_id_token}",
        "X-User-Uid": firebase_test_uid
    }
    review_id, source_id = submit_review(headers)

    payload = {
        "sourceId": source_id,
        "organizationId": str(uuid.uuid4()),
        "title": "Reply Title",
        "content": "Reply content",
        "rating": {"value": 5},
        "url": "http://example.com"
    }
    resp = requests.post(
        f"{BASE_URL}/api/review/reply/{review_id}",
        headers=headers,
        json=payload
    )
    resp.raise_for_status()
    data = resp.json()
    assert "reviewId" in data, "Expected `reviewId` in reply response"


def test_react_review(firebase_test_id_token, firebase_test_uid):
    headers = {
        "Authorization": f"Bearer {firebase_test_id_token}",
        "X-User-Uid": firebase_test_uid
    }
    review_id, source_id = submit_review(headers)

    payload = {
        "sourceId": source_id,
        "reviewId": review_id,
        "reaction": {
            "value": "L",
            "type": "LIKE"
        }
    }
    resp = requests.post(f"{BASE_URL}/api/review/react", headers=headers, json=payload)
    if resp.status_code != 200:
        print("React response:", resp.status_code, resp.text)
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()
    assert data.get("reviewId") == review_id, "React did not return expected reviewId"