import io
import os

from mutagen import File as MutagenFile

DURATION_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.mp4'}


def extract_duration_seconds(fileobj, filename=''):
    extension = os.path.splitext(filename or '')[1].lower()
    if extension and extension not in DURATION_EXTENSIONS:
        return None

    try:
        position = fileobj.tell()
    except (AttributeError, OSError):
        position = None

    try:
        if hasattr(fileobj, 'seek'):
            fileobj.seek(0)
        audio = MutagenFile(fileobj)
        if audio is not None and audio.info and audio.info.length:
            return max(0, int(round(audio.info.length)))
    except Exception:
        return None
    finally:
        if position is not None and hasattr(fileobj, 'seek'):
            try:
                fileobj.seek(position)
            except (AttributeError, OSError):
                pass

    return None


def extract_duration_from_bytes(data, filename=''):
    if not data:
        return None
    return extract_duration_seconds(io.BytesIO(data), filename)
