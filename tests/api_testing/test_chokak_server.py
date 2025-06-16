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
    assert isinstance(data, list), "Ожидаем список отзывов"
    for review in data:
        assert "id" in review
        assert "rating" in review
        assert "text" in review
        assert review.get("userUid") == firebase_test_uid
