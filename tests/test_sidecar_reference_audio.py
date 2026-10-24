"""Sidecar engines only ever receive WAV/FLAC references.

A WhatsApp voice note (Ogg Opus) cloned on OmniVoice, whose loader falls back
to ffmpeg, but VoxCPM2 and CosyVoice opened it with their own libsndfile and
failed with "Format not recognised". The parent now converts every other
container once and hands the sidecar a cached WAV.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from services import tts_backend
from services.subprocess_backend import SubprocessBackend


@pytest.fixture(autouse=True)
def _isolated_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(tts_backend, "_sidecar_reference_cache_dir", lambda: str(tmp_path / "cache"))


def _tone(seconds: float, sr: int) -> np.ndarray:
    t = np.arange(int(seconds * sr)) / sr
    return (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)


def _voice_note(tmp_path: Path) -> str:
    path = tmp_path / "voice-note.ogg"
    sf.write(path, _tone(1.0, 48000), 48000, format="OGG", subtype="OPUS")
    return str(path)


@pytest.mark.parametrize(("name", "fmt"), [("clip.wav", "WAV"), ("clip.flac", "FLAC")])
def test_wav_and_flac_references_pass_through_unchanged(tmp_path, name, fmt):
    path = tmp_path / name
    sf.write(path, _tone(0.5, 24000), 24000, format=fmt)

    assert tts_backend.sidecar_readable_reference(str(path)) == str(path)


def test_an_opus_voice_note_becomes_a_wav_any_sidecar_can_open(tmp_path):
    converted = tts_backend.sidecar_readable_reference(_voice_note(tmp_path))

    info = sf.info(converted)
    assert info.format == "WAV"
    assert info.samplerate == 48000
    assert info.duration == pytest.approx(1.0, abs=0.1)


def test_a_reference_is_decoded_only_once(monkeypatch, tmp_path):
    note = _voice_note(tmp_path)
    first = tts_backend.sidecar_readable_reference(note)
    monkeypatch.setattr(tts_backend, "_read_reference_mono",
                        lambda _path: pytest.fail("decoded the same clip twice"))

    assert tts_backend.sidecar_readable_reference(note) == first


def test_an_undecodable_reference_is_passed_through_for_the_engine_to_report(tmp_path):
    junk = tmp_path / "broken.ogg"
    junk.write_bytes(b"not audio at all")

    assert tts_backend.sidecar_readable_reference(str(junk)) == str(junk)


def test_every_sidecar_engine_receives_a_wav_reference(monkeypatch, tmp_path):
    from services import model_manager

    class FakeSidecar(SubprocessBackend):
        id = "_fake_sidecar"
        sample_rate = 24000
        supported_languages = ["multi"]

        @classmethod
        def is_available(cls):
            return True, "ready"

        @classmethod
        def venv_python(cls):
            return Path(sys.executable)

        @classmethod
        def sidecar_script(cls):
            return Path("unused-sidecar.py")

    class Sent(Exception):
        pass

    sent: dict = {}

    def capture(message):
        sent.update(message)
        raise Sent

    backend = FakeSidecar()
    monkeypatch.setattr(model_manager, "running_on_gpu_pool", lambda: True)
    monkeypatch.setattr(backend, "_spawn", lambda: None)
    monkeypatch.setattr(backend, "_send", capture)

    with pytest.raises(Sent):
        backend.generate("Hello", ref_audio=_voice_note(tmp_path))

    assert sf.info(sent["ref_audio"]).format == "WAV"


def test_voxcpm2_prepares_the_converted_voice_note(tmp_path):
    kw = {"ref_audio": _voice_note(tmp_path)}

    tts_backend.prepare_voxcpm_reference(kw)

    assert sf.info(kw["ref_audio"]).format == "WAV"
