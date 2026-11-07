"""FFmpeg rendering adapter (video/audio compose)."""

import shutil
import subprocess


def probe():
    return shutil.which("ffmpeg") is not None


def capabilities():
    return ["render.ffmpeg", "render.concat", "render.thumbnail"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "ffmpeg not installed"}
    if action == "render.ffmpeg":
        args = params.get("args", [])
        try:
            r = subprocess.run(["ffmpeg", "-y"] + args, capture_output=True, text=True, timeout=600)
            return {"status": "ok" if r.returncode == 0 else "failed", "returncode": r.returncode,
                    "stderr": r.stderr[-1500:]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    if action == "render.concat":
        # params: inputs (list of files), out
        inputs = params.get("inputs", [])
        out = params.get("out", "out.mp4")
        listfile = params.get("listfile", "concat.txt")
        with open(listfile, "w") as f:
            for i in inputs:
                f.write(f"file '{i}'\n")
        try:
            r = subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", out],
                capture_output=True, text=True, timeout=600,
            )
            return {"status": "ok" if r.returncode == 0 else "failed", "out": out, "returncode": r.returncode}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    return {"status": "refused", "reason": f"unknown action {action}"}