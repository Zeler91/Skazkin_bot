import pytest
from src.services.gigachat_service import GigaChatService

class DummyClient:
    def __init__(self, response):
        self.response = response
        self.token = "dummy-token"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def chat(self, chat):
        return self.response


def test_generate_story_success(monkeypatch):
    fake_response = type("obj", (), {
        "choices": [type("msg", (), {"message": type("m", (), {"content": "Сказка о дружбе"})})]
    })

    service = GigaChatService()

    # подменяем _get_client, чтобы он возвращал наш dummy-клиент
    monkeypatch.setattr(service, "_get_client", lambda: DummyClient(fake_response))

    story = service.generate_story("Придумай сказку про дружбу")
    assert "Сказка" in story


def test_generate_story_failure(monkeypatch):
    service = GigaChatService()

    def broken_client():
        raise Exception("Ошибка API")

    monkeypatch.setattr(service, "_get_client", broken_client)

    story = service.generate_story("Любая сказка")
    assert story is None
