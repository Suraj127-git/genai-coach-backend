import uuid

def make_key(user_id: str, extension: str) -> str:
    ext = extension.lower().strip(".")
    if ext not in {"m4a", "mp3", "wav"}:
        raise ValueError("Unsupported extension")
    return f"recordings/{user_id}/{uuid.uuid4()}.{ext}"

