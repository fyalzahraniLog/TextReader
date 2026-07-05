import io
from urllib.parse import unquote

from fastapi.testclient import TestClient
from PIL import Image

import app as server_app

client = TestClient(server_app.app)


def _png_bytes(size=(100, 40), color=(255, 255, 255)):
    image = Image.new("RGB", size, color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


async def _fake_synthesize(_text):
    return b"fake-mp3-bytes"


def test_happy_path_returns_audio_and_headers(monkeypatch):
    monkeypatch.setattr(server_app, "_ocr", lambda _image_bytes: "Hello world")
    monkeypatch.setattr(server_app, "_translate", lambda text: text)  # identity: no network call
    monkeypatch.setattr(server_app, "_synthesize", _fake_synthesize)

    response = client.post(
        "/process",
        files={"file": ("capture.png", _png_bytes(), "image/png")},
        data={"game": ""},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-mp3-bytes"
    assert unquote(response.headers["x-source-text"]) == "Hello world"
    assert unquote(response.headers["x-output-text"]) == "Hello world"


def test_game_glossary_terms_are_pinned_and_restored(monkeypatch):
    monkeypatch.setattr(server_app, "_ocr", lambda _image_bytes: "The Rogue attacks.")
    monkeypatch.setattr(server_app, "_translate", lambda text: text)  # identity passthrough
    monkeypatch.setattr(server_app, "_synthesize", _fake_synthesize)

    response = client.post(
        "/process",
        files={"file": ("capture.png", _png_bytes(), "image/png")},
        data={"game": "pathfinder-wotr"},
    )

    assert response.status_code == 200
    output_text = unquote(response.headers["x-output-text"])
    assert "محتال" in output_text  # general glossary: Rogue -> محتال


def test_no_text_detected_returns_422(monkeypatch):
    monkeypatch.setattr(server_app, "_ocr", lambda _image_bytes: "")

    response = client.post(
        "/process",
        files={"file": ("capture.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 422


def test_bad_image_returns_400():
    response = client.post(
        "/process",
        files={"file": ("capture.png", io.BytesIO(b"not a real png"), "image/png")},
    )

    assert response.status_code == 400


def test_oversized_image_returns_400(monkeypatch):
    monkeypatch.setattr(server_app, "MAX_IMAGE_BYTES", 10)

    response = client.post(
        "/process",
        files={"file": ("capture.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 400


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_games_lists_known_game():
    response = client.get("/games")

    assert response.status_code == 200
    assert "pathfinder-wotr" in response.json()["games"]
