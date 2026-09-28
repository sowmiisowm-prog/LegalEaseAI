from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "LegalEase"

    assert data["status"] == "running"


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_without_api_key(
    monkeypatch
):

    monkeypatch.setenv(
        "GEMINI_API_KEY",
        ""
    )

    from backend.services.gemini_generator import (
        GeminiDocumentGenerator,
    )

    generator = (
        GeminiDocumentGenerator()
    )

    text, provider = (
        generator.generate_document(

            document_type=
                "Freelance Work Contract",

            parties=(
                "Client: ABC Technologies Pvt. Ltd.; "
                "Freelancer: Arun Kumar"
            ),

            terms=(
                "Payment: Rs. 25,000; "
                "Completion: 30 days"
            ),

            effective_date=
                "1 October 2026",
        )
    )

    assert text

    assert (
        "Freelance Work Contract"
        in text
    )

    assert provider == "local-fallback"