import os
import uuid
from io import BytesIO
from locust import HttpUser, task, between, SequentialTaskSet
from dotenv import load_dotenv


load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
API_BASE = os.getenv("API_BASE_URL")

class ImageWorkflow(SequentialTaskSet):
    token = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_start(self):
        if not ImageWorkflow.token:
            url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
            resp = self.client.post(
                url=url,
                json={
                    "email": os.getenv("FIREBASE_TEST_EMAIL"),
                    "password": os.getenv("FIREBASE_TEST_PASSWORD"),
                    "returnSecureToken": True
                },
                name="Firebase SignIn"
            )
            resp.raise_for_status()
            ImageWorkflow.token = resp.json()["idToken"]

        self.auth_headers = {"Authorization": f"Bearer {ImageWorkflow.token}"}

    @task
    def upload_image(self):
        fname = f"test_image_{uuid.uuid4().hex}.jpg"
        img = BytesIO()
        img.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 1024 + b"\xFF\xD9")
        img.seek(0)
        with self.client.post(
            "/uploads/images/images",
            files={"file": (fname, img, "image/jpeg")},
            headers=self.auth_headers,
            name="Upload Image",
            catch_response=True
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Upload failed: {response.status_code}")
                return
            body = response.json()
            url = body["url"]
            if url.startswith("/"):
                url = API_BASE.rstrip("/") + url
            self.uploaded = {"url": url, "filename": fname}

    @task
    def get_image(self):
        if not hasattr(self, "uploaded"):
            return
        url = self.uploaded.get("url")
        corrected_url = url.replace("/images/", "/uploads/images/")
        self.client.get(corrected_url, name="Get Image")

    @task
    def delete_image(self):
        if not hasattr(self, "uploaded"):
            return
        url = self.uploaded["url"]
        corrected_url = url.replace("/images/", "/uploads/images/")
        self.client.delete(corrected_url, name="Delete Image", headers=self.auth_headers)

class ImageServerUser(HttpUser):
    weight = 1
    host = API_BASE
    tasks = [ImageWorkflow]
    wait_time = between(1, 3)

class MainServerUser(HttpUser):
    weight = 3
    host = API_BASE
    wait_time = between(1, 3)

    @task(2)
    def get_cities(self):
        self.client.get("/api/places/cities")

    @task(2)
    def get_categories(self):
        self.client.get("/api/places/categories")

    @task(4)
    def post_organizations(self):
        payload = {
            "cityId": 1,
            "type": "RESTAURANTS_AND_CAFES",
            "criteria": "RELEVANCE",
            "to": 2
        }
        self.client.post("/api/organizations/query", json=payload)
