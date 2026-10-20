"""
TTS Service for AI English Voice Coach
Supports:
1. Edge-TTS (100% Free, High Quality Neural US/UK/AU voices, adjustable speed)
2. ElevenLabs (Ultra-realistic Neural Voices using eleven_flash_v2_5 for low latency & cost efficiency)
"""

import asyncio
import hashlib
import os
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "audio_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

EDGE_VOICE_MAP = {
    "us_female": "en-US-JennyNeural",
    "us_male": "en-US-GuyNeural",
    "uk_female": "en-GB-SoniaNeural",
    "uk_male": "en-GB-RyanNeural",
    "au_female": "en-AU-NatashaNeural",
}

ELEVEN_VOICE_MAP = {
    "us_female": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "us_male": "pNInz6obpgDQGcFmaJgB",    # Adam
    "host_b": "XLXcyPK1jTjw1pYLLcM9",
}

def get_audio_cache_path(text: str, engine: str, voice: str, speed: str) -> Path:
    key = f"{engine}|{voice}|{speed}|{text}"
    h = hashlib.md5(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.mp3"


async def synthesize_edge_tts_async(text: str, voice: str, speed: str = "1.0") -> bytes:
    import edge_tts
    rate_str = "+0%"
    try:
        s = float(speed)
        pct = int((s - 1.0) * 100)
        rate_str = f"{pct:+d}%"
    except Exception:
        pass

    target_voice = EDGE_VOICE_MAP.get(voice, voice)
    comm = edge_tts.Communicate(text=text, voice=target_voice, rate=rate_str)
    chunks = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


def synthesize_elevenlabs(text: str, voice: str, api_key: str = "") -> bytes:
    from elevenlabs.client import ElevenLabs
    key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise ValueError("ELEVENLABS_API_KEY is missing")

    target_voice_id = ELEVEN_VOICE_MAP.get(voice, voice)
    client = ElevenLabs(api_key=key)

    # Use eleven_flash_v2_5 for lowest latency & 50% credit cost
    audio_stream = client.text_to_speech.convert(
        voice_id=target_voice_id,
        text=text,
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128"
    )
    return b"".join(audio_stream)


def generate_coach_speech(text: str, engine: str = "edge_tts", voice: str = "us_female", speed: str = "1.0", api_key: str = "") -> tuple[bytes, str]:
    """
    Returns (audio_bytes, cache_filename)
    """
    cache_path = get_audio_cache_path(text, engine, voice, speed)
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return cache_path.read_bytes(), cache_path.name

    audio_bytes = None
    if engine == "elevenlabs":
        try:
            audio_bytes = synthesize_elevenlabs(text, voice, api_key)
        except Exception as e:
            print(f"[ElevenLabs TTS Failed]: {e}, falling back to Edge-TTS...")
            audio_bytes = asyncio.run(synthesize_edge_tts_async(text, voice, speed))
    else:
        audio_bytes = asyncio.run(synthesize_edge_tts_async(text, voice, speed))

    if audio_bytes:
        cache_path.write_bytes(audio_bytes)
        return audio_bytes, cache_path.name

    raise RuntimeError("Failed to generate tutor speech")
