"""Kokoro-FastAPI TTS adapter (replaces 437-line stdlib server)."""

import os
import shutil

import httpx

SERVICE_URL = os.environ.get("KOKORO_URL", "http://127.0.0.1:8880").rstrip("/")


def probe():
    # Available if the service responds OR kokoro package installed
    try:
        r = httpx.get(f"{SERVICE_URL}/health", timeout=3.0)
        if r.status_code == 200:
            return True
    except Exception:
        pass
    try:
        import kokoro  # noqa: F401
        return True
    except ImportError:
        return False


def capabilities():
    return ["tts.synthesize", "tts.voices"]


def run(action, params):
    if action == "tts.voices":
        try:
            r = httpx.get(f"{SERVICE_URL}/v1/audio/voices", timeout=5.0)
            return {"status": "ok", "voices": r.json()} if r.status_code == 200 else {"status": "error", "code": r.status_code}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    if action != "tts.synthesize":
        return {"status": "refused", "reason": f"unknown action {action}"}
    text = params.get("text", "")
    voice = params.get("voice", "af_heart")
    out = params.get("out", "out.wav")
    try:
        r = httpx.post(
            f"{SERVICE_URL}/v1/audio/speech",
            json={"model": "kokoro", "input": text, "voice": voice, "response_format": "wav"},
            timeout=120.0,
        )
        if r.status_code == 200:
            with open(out, "wb") as f:
                f.write(r.content)
            return {"status": "ok", "out": out, "bytes": len(r.content)}
        return {"status": "error", "code": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}