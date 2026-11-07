"""Docling ingestion adapter (replaces PDFBox/PaddleOCR)."""

def probe():
    try:
        import docling  # noqa: F401
        return True
    except ImportError:
        return False


def capabilities():
    return ["ingest.convert", "ingest.extract"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "docling not installed"}
    if action not in ("ingest.convert", "ingest.extract"):
        return {"status": "refused", "reason": f"unknown action {action}"}
    path = params.get("path")
    if not path:
        return {"status": "refused", "reason": "path required"}
    try:
        from docling.document_converter import DocumentConverter

        conv = DocumentConverter()
        result = conv.convert(path)
        md = result.document.export_to_markdown()
        out = params.get("out")
        if out:
            with open(out, "w") as f:
                f.write(md)
        return {"status": "ok", "chars": len(md), "out": out}
    except Exception as e:
        return {"status": "error", "reason": str(e)}