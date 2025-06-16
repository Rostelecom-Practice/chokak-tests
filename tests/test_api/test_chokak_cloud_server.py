import os
import requests
from io import BytesIO
import pytest
import uuid

API_BASE = os.getenv("API_BASE_URL")


@pytest.fixture(scope="session")
def auth_headers(firebase_test_id_token):
    return {"Authorization": f"Bearer {firebase_test_id_token}"}


@pytest.fixture(scope="session")
def test_uploaded_image(auth_headers):
    fname = f"test_image_{uuid.uuid4().hex}.jpg"

    img = BytesIO()
    img.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 1024 + b"\xFF\xD9")
    img.seek(0)

    resp = requests.post(
        url=f"{API_BASE}/uploads/images/images",
        files={"file": (fname, img, "image/jpeg")},
        headers=auth_headers
    )
    resp.raise_for_status()
    body = resp.json()
    url = body["url"]
    if not url.startswith("http"):
        if not url.startswith("/uploads/"):
            url = f"/uploads/{url.lstrip('/')}"
        url = API_BASE.rstrip("/") + url

    data = {"url": url, "filename": fname}

    yield data

    delete_resp = requests.delete(data["url"], headers=auth_headers)
    assert delete_resp.status_code in (200, 204, 404), "Failed to delete test image"

def test_uploaded_image_is_accessible(test_uploaded_image):
    url = test_uploaded_image["url"]
    resp = requests.get(url)
    assert resp.status_code == 200, f"Image not available at URL: {url}"
    assert resp.headers["Content-Type"].startswith("image/"), "Expect content like image/*"
