"""`ops content` command group (Phase 3 content factory)."""

import click

from desktop_ops.adapters import kokoro, ffmpeg, thumbnail, docling


@click.group()
def content():
    """Content factory commands."""


@content.command("tts")
@click.option("--text", required=True)
@click.option("--voice", default="af_heart")
@click.option("--out", default="out.wav")
def tts_cmd(text, voice, out):
    click.echo(kokoro.run("tts.synthesize", {"text": text, "voice": voice, "out": out}))


@content.command("thumbnail")
@click.option("--text", default="")
@click.option("--out", default="thumb.png")
@click.option("--w", default=1280, type=int)
@click.option("--h", default=720, type=int)
def thumb_cmd(text, out, w, h):
    click.echo(thumbnail.run("thumbnail.create", {"text": text, "out": out, "w": w, "h": h}))


@content.command("ingest")
@click.option("--path", required=True)
@click.option("--out", default=None)
def ingest_cmd(path, out):
    click.echo(docling.run("ingest.convert", {"path": path, "out": out}))


@content.command("ffmpeg")
@click.option("--args", default="", help="Comma-separated ffmpeg args")
def ffmpeg_cmd(args):
    click.echo(ffmpeg.run("render.ffmpeg", {"args": args.split(",") if args else []}))