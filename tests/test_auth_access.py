import os
import requests
from io import BytesIO

def test_upload_image(firebase_test_id_token):
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
