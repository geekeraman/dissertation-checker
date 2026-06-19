"""API route handlers."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.api.schemas import ReportSchema, HealthResponse
from app.core.config import settings
from app.parser.docx_parser import parse_docx
from app.runner import CheckerRunner
from app.checkers.structure import StructureChecker
from app.checkers.formatting import FormattingChecker
from app.checkers.captions import CaptionChecker
from app.checkers.spacing import SpacingChecker
from app.checkers.citations import CitationChecker

import os
import tempfile

router = APIRouter()


def create_runner() -> CheckerRunner:
    runner = CheckerRunner()
    runner.register(StructureChecker())
    runner.register(FormattingChecker())
    runner.register(CaptionChecker())
    runner.register(SpacingChecker())
    runner.register(CitationChecker())
    return runner


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@router.post("/check", response_model=ReportSchema)
async def check_dissertation(
    file: UploadFile = File(...),
    doc_type: str = Form(default="thesis_science"),
):
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {settings.max_upload_size_mb} MB",
        )

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        document = parse_docx(tmp_path, doc_type)
        runner = create_runner()
        report = runner.run(document, file.filename)
        return report
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error parsing document: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
