from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ResearchIQ"}

def test_upload_non_pdf_fails():
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"Invalid text content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF files" in response.text
