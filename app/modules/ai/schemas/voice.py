from pydantic import BaseModel

class VoiceText(BaseModel):
    text: str

class VoiceAudioUri(BaseModel):
    uri: str

