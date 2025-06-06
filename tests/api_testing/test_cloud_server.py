import os
import requests
from io import BytesIO
import pytest

uploaded_image_url = None  # глобальная переменная для хранения URL
filename = None

@pytest.mark.order(1)
def test_upload_image(firebase_test_id_token):
    global uploaded_image_url, filename

    headers = {
        "Authorization": f"Bearer {firebase_test_id_token}"
    }

    image_bytes = BytesIO()
    image_bytes.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 1024 + b"\xFF\xD9")
    image_bytes.seek(0)

    response = requests.post(
        url=os.getenv("API_BASE_URL") + "/uploads/images/images",
        files={"file": ("test_image.jpg", image_bytes, "image/jpeg")},
        headers=headers
    )

    assert response.status_code == 201, f"Upload failed: {response.status_code}, {response.text}"

    image_url = response.json()["url"]
    uploaded_image_url = os.getenv("API_BASE_URL") + "/uploads" + image_url
    filename = image_url.split("/")[-1]

@pytest.mark.order(2)
def test_get_uploaded_image():
    global uploaded_image_url
    assert uploaded_image_url is not None, "Image not uploaded in previous test"

    response = requests.get(uploaded_image_url)
    assert response.status_code == 200, f"Image not found: {response.status_code}"
    assert response.headers["Content-Type"].startswith("image/"), "Invalid content type"

@pytest.mark.order(3)
def test_delete_uploaded_image(firebase_test_id_token):
    global uploaded_image_url
    assert uploaded_image_url is not None, "Image not uploaded in previous test"

    headers = {
        "Authorization": f"Bearer {firebase_test_id_token}"
    }

    response = requests.delete(uploaded_image_url, headers=headers)
    assert response.status_code == 204, f"Delete failed: {response.status_code}, {response.text}"

    check_response = requests.get(uploaded_image_url)
    assert check_response.status_code == 404, "Image still accessible after deletion"
