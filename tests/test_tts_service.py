import os
import pytest
from src.services.tts_service import TTSService

def test_tts_service_disabled(monkeypatch):
    service = TTSService()
    service.enabled = False
    result = service.synthesize_speech("Тестовая сказка")
    assert result is None


def test_tts_cleanup_temp_file(tmp_path):
    service = TTSService()
    tmp_file = tmp_path / "test.mp3"
    tmp_file.write_text("audio data")

    assert tmp_file.exists()
    service.cleanup_temp_file(str(tmp_file))
    assert not tmp_file.exists()
