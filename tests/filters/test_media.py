import wave

import pytest
from mutagen.id3 import TALB, TDRC, TIT2, TPE1
from mutagen.wave import WAVE

from organize import Config
from organize.filters import media


def make_wav(path, seconds=2, **tags):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\x00\x00" * 8000 * seconds)
    if tags:
        audio = WAVE(path)
        audio.add_tags()
        frames = {"title": TIT2, "artist": TPE1, "album": TALB, "year": TDRC}
        for key, value in tags.items():
            audio.tags.add(frames[key](encoding=3, text=value))
        audio.save()


@pytest.fixture(autouse=True)
def no_spotlight(monkeypatch):
    monkeypatch.setattr(media, "_from_spotlight", lambda path: {})


def test_reads_tags(tmp_path):
    path = tmp_path / "song.wav"
    make_wav(path, title="Blue", artist="AC/DC", album="Live", year="1992-05-01")
    assert media.media_metadata(path) == {
        "title": "Blue",
        "artist": "AC/DC",
        "album": "Live",
        "year": "1992",
        "duration": "2",
    }


def test_describe():
    text = media.describe({"title": "Talk", "duration": "60"})
    assert text == "Title: Talk\nDuration: 60 seconds"
    assert media.describe({}) is None


def test_not_media(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    assert media.media_metadata(path) == {}


def test_sort_music_by_artist(tmp_path):
    make_wav(tmp_path / "a.wav", artist="AC/DC", album="Live")
    make_wav(tmp_path / "b.wav", artist="Abba")
    Config.from_string(
        f"""
        rules:
          - locations: "{tmp_path}"
            subfolders: false
            filters:
              - media
            actions:
              - move: "{tmp_path}/Music/{{media.artist}}/{{media.album}}/"
        """
    ).execute(simulate=False)
    assert (tmp_path / "Music/AC-DC/Live/a.wav").is_file()
    assert (tmp_path / "Music/Abba/Unknown/b.wav").is_file()
