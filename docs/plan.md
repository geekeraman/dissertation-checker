# Dissertation Checker — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web service that checks student dissertations (.docx) against GOST 7.32-2017 formatting standards and produces a visual compliance report.

**Architecture:** Plugin-based checker architecture. Each checker is an independent module implementing `BaseChecker`. A runner orchestrates all checkers. Python FastAPI backend + React/Vite frontend.

**Tech Stack:** Python 3.11+, FastAPI, python-docx, React 18, Vite, TypeScript, Docker

**Spec:** `docs/design.md`

---

## Parallel Development Tracks

This plan is organized into 3 parallel tracks. After Task 1 (shared foundation), all tracks proceed independently.

| Track | Developer | Tasks |
|-------|-----------|-------|
| Shared | All (Day 1) | Task 1 |
| A: Core + Structure + Formatting | Dev A | Tasks 2, 3, 4 |
| B: Captions + Spacing + Frontend | Dev B | Tasks 5, 6, 7 |
| C: Citations + Integration + DevOps | Dev C | Tasks 8, 9, 10 |

---

## Task 1: Shared Foundation (All Developers — Day 1)

**Files:**
- Create: `dissertation-checker/backend/pyproject.toml`
- Create: `dissertation-checker/backend/app/__init__.py`
- Create: `dissertation-checker/backend/app/core/__init__.py`
- Create: `dissertation-checker/backend/app/core/config.py`
- Create: `dissertation-checker/backend/app/core/models.py`
- Create: `dissertation-checker/backend/app/parser/__init__.py`
- Create: `dissertation-checker/backend/app/parser/structures.py`
- Create: `dissertation-checker/backend/app/checkers/__init__.py`
- Create: `dissertation-checker/backend/app/checkers/base.py`
- Create: `dissertation-checker/backend/app/api/__init__.py`
- Create: `dissertation-checker/backend/app/api/schemas.py`
- Create: `dissertation-checker/backend/app/runner.py`
- Create: `dissertation-checker/backend/app/main.py`
- Create: `dissertation-checker/backend/app/api/routes.py`
- Create: `dissertation-checker/backend/tests/__init__.py`
- Create: `dissertation-checker/backend/tests/conftest.py`
- Create: `dissertation-checker/.gitignore`

- [ ] **Step 1: Create project directory and git repo**

```bash
mkdir -p dissertation-checker/backend/app/{api,core,parser,checkers}
mkdir -p dissertation-checker/backend/tests/fixtures
cd dissertation-checker
git init
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
dist/
build/
.eggs/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
frontend/dist/

# Uploads
backend/uploads/
backend/tmp/
```

- [ ] **Step 3: Create pyproject.toml**

```toml
[project]
name = "dissertation-checker"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "python-multipart>=0.0.9",
    "python-docx>=1.1.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.4.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
target-version = "py311"
line-length = 100
```

- [ ] **Step 4: Create core/models.py — domain models**

```python
"""Domain models for the dissertation checker."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
import uuid


@dataclass
class IssueLocation:
    paragraph_index: int | None = None
    page_number: int | None = None
    section_name: str | None = None
    context_text: str = ""


@dataclass
class Issue:
    severity: Literal["error", "warning", "info"]
    category: str
    checker: str
    location: IssueLocation
    message: str
    suggestion: str
    rule_ref: str = ""


@dataclass
class Report:
    id: str
    filename: str
    checked_at: datetime
    doc_type: str
    total_issues: int
    issues_by_severity: dict[str, int]
    issues_by_category: dict[str, int]
    issues: list[Issue]

    @staticmethod
    def from_issues(
        issues: list[Issue], filename: str, doc_type: str
    ) -> "Report":
        severity_counts: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
        category_counts: dict[str, int] = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        return Report(
            id=str(uuid.uuid4()),
            filename=filename,
            checked_at=datetime.utcnow(),
            doc_type=doc_type,
            total_issues=len(issues),
            issues_by_severity=severity_counts,
            issues_by_category=category_counts,
            issues=issues,
        )
```

- [ ] **Step 5: Create parser/structures.py — parsed document structures**

```python
"""Data structures for parsed DOCX documents."""

from dataclasses import dataclass, field


@dataclass
class ParsedParagraph:
    text: str
    style_name: str
    is_heading: bool
    heading_level: int | None  # 1-9 if heading, None otherwise
    font_name: str | None
    font_size: float | None  # in points
    bold: bool | None
    alignment: str | None  # "left", "center", "right", "justify"
    line_spacing: float | None  # e.g., 1.5
    first_line_indent: float | None  # in cm
    has_page_break_before: bool = False
    paragraph_index: int = 0


@dataclass
class DocumentSection:
    name: str
    heading: str
    start_paragraph_index: int
    end_paragraph_index: int
    level: int  # heading level


@dataclass
class Figure:
    number: str | None  # e.g., "1.1"
    title: str | None
    paragraph_index: int  # where the figure is referenced/located
    caption_paragraph_index: int | None  # paragraph index of caption
    has_caption: bool = False
    caption_position: str | None = None  # "above" or "below"


@dataclass
class Table:
    number: str | None
    title: str | None
    paragraph_index: int
    caption_paragraph_index: int | None
    has_caption: bool = False
    caption_position: str | None = None  # "above" or "below"


@dataclass
class Reference:
    text: str
    paragraph_index: int


@dataclass
class DocumentMetadata:
    title: str | None = None
    author: str | None = None
    language: str | None = None


@dataclass
class DocProperties:
    left_margin_cm: float | None = None
    right_margin_cm: float | None = None
    top_margin_cm: float | None = None
    bottom_margin_cm: float | None = None
    default_font_name: str | None = None
    default_font_size: float | None = None
    default_line_spacing: float | None = None
    page_width_cm: float | None = None
    page_height_cm: float | None = None


@dataclass
class ParsedDocument:
    doc_type: str  # "thesis_humanities" | "thesis_science" | "project"
    paragraphs: list[ParsedParagraph] = field(default_factory=list)
    sections: list[DocumentSection] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    page_count: int = 0
    page_count_body: int = 0
    properties: DocProperties = field(default_factory=DocProperties)
```

- [ ] **Step 6: Create checkers/base.py — checker interface**

```python
"""Base checker interface for all dissertation checkers."""

from abc import ABC, abstractmethod

from app.core.models import Issue
from app.parser.structures import ParsedDocument


class BaseChecker(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def check(self, document: ParsedDocument) -> list[Issue]:
        """Run checks against the parsed document and return issues found."""
        ...
```

- [ ] **Step 7: Create core/config.py**

```python
"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Dissertation Checker"
    max_upload_size_mb: int = 50
    cors_origins: list[str] = ["http://localhost:5173"]
    temp_dir: str = "tmp"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 8: Create api/schemas.py — Pydantic API models**

```python
"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class IssueLocationSchema(BaseModel):
    paragraph_index: int | None = None
    page_number: int | None = None
    section_name: str | None = None
    context_text: str = ""


class IssueSchema(BaseModel):
    severity: Literal["error", "warning", "info"]
    category: str
    checker: str
    location: IssueLocationSchema
    message: str
    suggestion: str
    rule_ref: str = ""


class ReportSchema(BaseModel):
    id: str
    filename: str
    checked_at: datetime
    doc_type: str
    total_issues: int
    issues_by_severity: dict[str, int]
    issues_by_category: dict[str, int]
    issues: list[IssueSchema]


class HealthResponse(BaseModel):
    status: str = "ok"
```

- [ ] **Step 9: Create runner.py — checker orchestrator**

```python
"""Runner that orchestrates all checkers."""

from app.checkers.base import BaseChecker
from app.core.models import Issue, Report
from app.parser.structures import ParsedDocument


class CheckerRunner:
    def __init__(self) -> None:
        self._checkers: list[BaseChecker] = []

    def register(self, checker: BaseChecker) -> None:
        self._checkers.append(checker)

    def run(self, document: ParsedDocument, filename: str) -> Report:
        all_issues: list[Issue] = []
        for checker in self._checkers:
            issues = checker.check(document)
            all_issues.extend(issues)
        return Report.from_issues(
            issues=all_issues,
            filename=filename,
            doc_type=document.doc_type,
        )
```

- [ ] **Step 10: Create main.py — FastAPI app**

```python
"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
```

- [ ] **Step 11: Create api/routes.py — API endpoints**

```python
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
```

- [ ] **Step 12: Create stub checker files so routes.py imports work**

Create minimal stubs for all 5 checkers (these will be fully implemented in later tasks):

`app/checkers/structure.py`:
```python
from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument

class StructureChecker(BaseChecker):
    name = "structure"
    description = "Validates document section order and required sections"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 3
```

`app/checkers/formatting.py`:
```python
from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument

class FormattingChecker(BaseChecker):
    name = "formatting"
    description = "Validates page layout, typography, and heading styles"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 4
```

`app/checkers/captions.py`:
```python
from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument

class CaptionChecker(BaseChecker):
    name = "captions"
    description = "Validates figure and table captions"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 5
```

`app/checkers/spacing.py`:
```python
from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument

class SpacingChecker(BaseChecker):
    name = "spacing"
    description = "Validates whitespace consistency"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 6
```

`app/checkers/citations.py`:
```python
from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument

class CitationChecker(BaseChecker):
    name = "citations"
    description = "Validates citation and reference formatting"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 8
```

- [ ] **Step 13: Create parser/docx_parser.py — stub**

```python
"""DOCX document parser — extracts structured data from .docx files."""

from app.parser.structures import ParsedDocument

def parse_docx(file_path: str, doc_type: str) -> ParsedDocument:
    """Parse a .docx file and return a ParsedDocument."""
    return ParsedDocument(doc_type=doc_type)  # Fully implemented in Task 2
```

- [ ] **Step 14: Create tests/conftest.py**

```python
"""Shared test fixtures."""

import pytest
from app.parser.structures import (
    ParsedDocument, ParsedParagraph, DocumentSection,
    Figure, Table, Reference, DocumentMetadata, DocProperties,
)


def make_paragraph(
    text: str = "Sample text",
    style_name: str = "Normal",
    is_heading: bool = False,
    heading_level: int | None = None,
    font_name: str | None = "Times New Roman",
    font_size: float | None = 14.0,
    bold: bool | None = False,
    alignment: str | None = "justify",
    line_spacing: float | None = 1.5,
    first_line_indent: float | None = 1.0,
    has_page_break_before: bool = False,
    paragraph_index: int = 0,
) -> ParsedParagraph:
    return ParsedParagraph(
        text=text, style_name=style_name, is_heading=is_heading,
        heading_level=heading_level, font_name=font_name, font_size=font_size,
        bold=bold, alignment=alignment, line_spacing=line_spacing,
        first_line_indent=first_line_indent,
        has_page_break_before=has_page_break_before,
        paragraph_index=paragraph_index,
    )


def make_document(
    doc_type: str = "thesis_science",
    paragraphs: list[ParsedParagraph] | None = None,
    sections: list[DocumentSection] | None = None,
    figures: list[Figure] | None = None,
    tables: list[Table] | None = None,
    references: list[Reference] | None = None,
    page_count: int = 50,
    page_count_body: int = 45,
    properties: DocProperties | None = None,
) -> ParsedDocument:
    return ParsedDocument(
        doc_type=doc_type,
        paragraphs=paragraphs or [],
        sections=sections or [],
        figures=figures or [],
        tables=tables or [],
        references=references or [],
        metadata=DocumentMetadata(),
        page_count=page_count,
        page_count_body=page_count_body,
        properties=properties or DocProperties(),
    )
```

- [ ] **Step 15: Install dependencies and verify**

```bash
cd dissertation-checker/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run: `python -c "from app.main import app; print('OK')"`
Expected: `OK`

- [ ] **Step 16: Commit shared foundation**

```bash
git add -A
git commit -m "feat: shared foundation — models, interfaces, app scaffold"
```

---

## Task 2: DOCX Parser Implementation (Dev A)

**Files:**
- Modify: `backend/app/parser/docx_parser.py`
- Create: `backend/tests/test_parser.py`

- [ ] **Step 1: Write parser tests**

```python
"""Tests for the DOCX parser."""

import pytest
from unittest.mock import patch, MagicMock
from app.parser.docx_parser import parse_docx
from app.parser.structures import ParsedDocument


class TestParseDocx:
    def test_returns_parsed_document_with_correct_doc_type(self, tmp_path):
        # Create a minimal .docx file for testing
        doc_path = tmp_path / "test.docx"
        from docx import Document
        doc = Document()
        doc.add_paragraph("Test paragraph")
        doc.save(str(doc_path))

        result = parse_docx(str(doc_path), "thesis_science")
        assert isinstance(result, ParsedDocument)
        assert result.doc_type == "thesis_science"

    def test_extracts_paragraphs(self, tmp_path):
        doc_path = tmp_path / "test.docx"
        from docx import Document
        doc = Document()
        doc.add_paragraph("First paragraph")
        doc.add_paragraph("Second paragraph")
        doc.save(str(doc_path))

        result = parse_docx(str(doc_path), "project")
        assert len(result.paragraphs) >= 2
        assert result.paragraphs[0].text == "First paragraph"

    def test_extracts_headings(self, tmp_path):
        doc_path = tmp_path / "test.docx"
        from docx import Document
        doc = Document()
        doc.add_heading("КІРІСПЕ", level=1)
        doc.add_paragraph("Body text")
        doc.save(str(doc_path))

        result = parse_docx(str(doc_path), "thesis_humanities")
        headings = [p for p in result.paragraphs if p.is_heading]
        assert len(headings) >= 1
        assert headings[0].heading_level == 1

    def test_extracts_document_properties(self, tmp_path):
        doc_path = tmp_path / "test.docx"
        from docx import Document
        doc = Document()
        doc.add_paragraph("Test")
        doc.save(str(doc_path))

        result = parse_docx(str(doc_path), "project")
        assert result.properties is not None

    def test_extracts_sections(self, tmp_path):
        doc_path = tmp_path / "test.docx"
        from docx import Document
        doc = Document()
        doc.add_heading("КІРІСПЕ", level=1)
        doc.add_paragraph("Introduction text")
        doc.add_heading("1 НЕГІЗГІ БӨЛІМ", level=1)
        doc.add_paragraph("Main body text")
        doc.save(str(doc_path))

        result = parse_docx(str(doc_path), "thesis_science")
        assert len(result.sections) >= 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_parser.py -v`
Expected: FAIL (parser returns empty ParsedDocument)

- [ ] **Step 3: Implement docx_parser.py**

```python
"""DOCX document parser — extracts structured data from .docx files."""

from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.parser.structures import (
    ParsedDocument, ParsedParagraph, DocumentSection,
    Figure, Table, Reference, DocumentMetadata, DocProperties,
)
import re


ALIGNMENT_MAP = {
    WD_ALIGN_PARAGRAPH.LEFT: "left",
    WD_ALIGN_PARAGRAPH.CENTER: "center",
    WD_ALIGN_PARAGRAPH.RIGHT: "right",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
    None: None,
}


def _extract_font_info(paragraph) -> tuple[str | None, float | None, bool | None]:
    """Extract font name, size, and bold from a paragraph's runs."""
    font_name = None
    font_size = None
    bold = None
    for run in paragraph.runs:
        if run.font.name and font_name is None:
            font_name = run.font.name
        if run.font.size and font_size is None:
            font_size = run.font.size.pt
        if run.font.bold is not None and bold is None:
            bold = run.font.bold
    return font_name, font_size, bold


def _detect_figures(doc: Document, paragraphs: list[ParsedParagraph]) -> list[Figure]:
    """Detect figures from document content and inline shapes."""
    figures = []
    figure_pattern = re.compile(r"[Сс]урет\s*(\d+(?:\.\d+)?)", re.UNICODE)

    for i, para in enumerate(paragraphs):
        match = figure_pattern.search(para.text)
        if match:
            has_image = False
            # Check for inline shapes in the original docx paragraph
            if i < len(doc.paragraphs):
                for run in doc.paragraphs[i].runs:
                    if run._element.findall(
                        './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'
                    ) or run._element.findall(
                        './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pict'
                    ):
                        has_image = True
                        break

            figures.append(Figure(
                number=match.group(1),
                title=para.text,
                paragraph_index=i,
                has_caption=True,
                caption_paragraph_index=i,
                caption_position="below",
            ))
    return figures


def _detect_tables(doc: Document, paragraphs: list[ParsedParagraph]) -> list[Table]:
    """Detect tables and their captions from the document."""
    tables = []
    table_pattern = re.compile(r"(?:Кесте|Таблица|Table)\s*(\d+(?:\.\d+)?)", re.UNICODE)

    for i, para in enumerate(paragraphs):
        match = table_pattern.search(para.text)
        if match:
            tables.append(Table(
                number=match.group(1),
                title=para.text,
                paragraph_index=i,
                has_caption=True,
                caption_paragraph_index=i,
                caption_position="above",
            ))
    return tables


def _detect_references(paragraphs: list[ParsedParagraph]) -> list[Reference]:
    """Detect reference entries after the references heading."""
    references = []
    in_references = False
    ref_headings = {"тізімі", "список", "references", "әдебиеттер"}

    for i, para in enumerate(paragraphs):
        if para.is_heading:
            lower = para.text.lower()
            if any(rh in lower for rh in ref_headings):
                in_references = True
                continue
            elif in_references and para.heading_level == 1:
                break

        if in_references and para.text.strip():
            references.append(Reference(text=para.text, paragraph_index=i))

    return references


def _build_sections(paragraphs: list[ParsedParagraph]) -> list[DocumentSection]:
    """Build document sections from headings."""
    sections = []
    for i, para in enumerate(paragraphs):
        if para.is_heading and para.heading_level == 1:
            sections.append(DocumentSection(
                name=para.text.strip(),
                heading=para.text.strip(),
                start_paragraph_index=i,
                end_paragraph_index=len(paragraphs) - 1,
                level=1,
            ))
    # Set end_paragraph_index for each section
    for j in range(len(sections) - 1):
        sections[j].end_paragraph_index = sections[j + 1].start_paragraph_index - 1
    return sections


def _extract_properties(doc: Document) -> DocProperties:
    """Extract document-level properties from section settings."""
    props = DocProperties()
    section = doc.sections[0] if doc.sections else None
    if section:
        if section.left_margin:
            props.left_margin_cm = section.left_margin.cm
        if section.right_margin:
            props.right_margin_cm = section.right_margin.cm
        if section.top_margin:
            props.top_margin_cm = section.top_margin.cm
        if section.bottom_margin:
            props.bottom_margin_cm = section.bottom_margin.cm
        if section.page_width:
            props.page_width_cm = section.page_width.cm
        if section.page_height:
            props.page_height_cm = section.page_height.cm

    # Try to get default font from styles
    default_style = doc.styles["Normal"] if "Normal" in [s.name for s in doc.styles] else None
    if default_style and default_style.font:
        props.default_font_name = default_style.font.name
        if default_style.font.size:
            props.default_font_size = default_style.font.size.pt

    return props


def _estimate_page_count(paragraphs: list[ParsedParagraph]) -> int:
    """Rough page count estimation based on paragraph content."""
    total_chars = sum(len(p.text) for p in paragraphs)
    # A4 with TNR 14pt 1.5 spacing ≈ 1800 chars per page
    return max(1, total_chars // 1800)


def parse_docx(file_path: str, doc_type: str) -> ParsedDocument:
    """Parse a .docx file and return a ParsedDocument."""
    doc = Document(file_path)
    paragraphs: list[ParsedParagraph] = []

    for idx, para in enumerate(doc.paragraphs):
        style_name = para.style.name if para.style else "Normal"
        is_heading = style_name.startswith("Heading") or "heading" in style_name.lower()
        heading_level = None
        if is_heading:
            try:
                heading_level = int(style_name.replace("Heading", "").replace("heading", "").strip())
            except (ValueError, TypeError):
                heading_level = 1

        font_name, font_size, bold = _extract_font_info(para)
        alignment = ALIGNMENT_MAP.get(para.alignment)

        line_spacing = None
        if para.paragraph_format.line_spacing:
            try:
                line_spacing = float(para.paragraph_format.line_spacing)
            except (ValueError, TypeError):
                pass

        first_line_indent = None
        if para.paragraph_format.first_line_indent:
            try:
                first_line_indent = para.paragraph_format.first_line_indent.cm
            except (ValueError, TypeError):
                pass

        has_page_break = False
        for run in para.runs:
            if run._element.findall(
                './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br[@{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type="page"]'
            ):
                has_page_break = True
                break

        paragraphs.append(ParsedParagraph(
            text=para.text,
            style_name=style_name,
            is_heading=is_heading,
            heading_level=heading_level,
            font_name=font_name,
            font_size=font_size,
            bold=bold,
            alignment=alignment,
            line_spacing=line_spacing,
            first_line_indent=first_line_indent,
            has_page_break_before=has_page_break,
            paragraph_index=idx,
        ))

    sections = _build_sections(paragraphs)
    figures = _detect_figures(doc, paragraphs)
    tables = _detect_tables(doc, paragraphs)
    references = _detect_references(paragraphs)
    properties = _extract_properties(doc)
    page_count = _estimate_page_count(paragraphs)

    return ParsedDocument(
        doc_type=doc_type,
        paragraphs=paragraphs,
        sections=sections,
        figures=figures,
        tables=tables,
        references=references,
        metadata=DocumentMetadata(
            title=doc.core_properties.title,
            author=doc.core_properties.author,
        ),
        page_count=page_count,
        page_count_body=page_count,
        properties=properties,
    )
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_parser.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/parser/docx_parser.py backend/tests/test_parser.py
git commit -m "feat: implement DOCX parser with paragraph, section, figure, table extraction"
```

---

## Task 3: StructureChecker (Dev A)

**Files:**
- Modify: `backend/app/checkers/structure.py`
- Create: `backend/tests/test_structure.py`

- [ ] **Step 1: Write StructureChecker tests**

```python
"""Tests for StructureChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.structure import StructureChecker
from app.parser.structures import DocumentSection


class TestStructureChecker:
    def setup_method(self):
        self.checker = StructureChecker()

    def test_no_issues_for_correct_structure(self):
        sections = [
            DocumentSection("Title", "TITLE PAGE", 0, 2, 1),
            DocumentSection("Abstract", "РЕФЕРАТ", 3, 8, 1),
            DocumentSection("Contents", "МАЗМҰНЫ", 9, 15, 1),
            DocumentSection("Introduction", "КІРІСПЕ", 16, 30, 1),
            DocumentSection("Main", "1 НЕГІЗГІ БӨЛІМ", 31, 80, 1),
            DocumentSection("Conclusion", "ҚОРЫТЫНДЫ", 81, 90, 1),
            DocumentSection("References", "ПАЙДАЛАНЫЛҒАН ӘДЕБИЕТТЕР ТІЗІМІ", 91, 100, 1),
        ]
        doc = make_document(sections=sections, page_count_body=50, doc_type="thesis_science")
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_missing_required_heading(self):
        sections = [
            DocumentSection("Title", "TITLE PAGE", 0, 2, 1),
            DocumentSection("Introduction", "КІРІСПЕ", 3, 30, 1),
        ]
        doc = make_document(sections=sections)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "missing" in i.message.lower() or "required" in i.message.lower()]
        assert len(missing) > 0

    def test_wrong_section_order(self):
        sections = [
            DocumentSection("Conclusion", "ҚОРЫТЫНДЫ", 0, 10, 1),
            DocumentSection("Introduction", "КІРІСПЕ", 11, 30, 1),
        ]
        doc = make_document(sections=sections)
        issues = self.checker.check(doc)
        order_issues = [i for i in issues if "order" in i.message.lower()]
        assert len(order_issues) > 0

    def test_structural_heading_numbered(self):
        paragraphs = [
            make_paragraph("1 МАЗМҰНЫ", is_heading=True, heading_level=1, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        numbered = [i for i in issues if "not numbered" in i.message.lower() or "number" in i.message.lower()]
        assert len(numbered) > 0

    def test_page_volume_below_minimum(self):
        doc = make_document(page_count_body=20, doc_type="thesis_science")
        issues = self.checker.check(doc)
        volume = [i for i in issues if "volume" in i.message.lower() or "page" in i.message.lower()]
        assert len(volume) > 0

    def test_page_volume_project_minimum(self):
        doc = make_document(page_count_body=30, doc_type="project")
        issues = self.checker.check(doc)
        volume = [i for i in issues if "volume" in i.message.lower() or "page" in i.message.lower()]
        assert len(volume) > 0

    def test_page_volume_humanities_minimum(self):
        doc = make_document(page_count_body=35, doc_type="thesis_humanities")
        issues = self.checker.check(doc)
        volume = [i for i in issues if "volume" in i.message.lower() or "page" in i.message.lower()]
        assert len(volume) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_structure.py -v`
Expected: FAIL (StructureChecker returns empty list)

- [ ] **Step 3: Implement StructureChecker**

```python
"""StructureChecker — validates document section order per GOST 7.32-2017 Sec. 6.4."""

import re
from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


REQUIRED_ORDER = [
    "title",
    "abstract",
    "contents",
    "introduction",
    "main",
    "conclusion",
    "references",
]

# Keywords for matching section headings (Kazakh + Russian variants)
SECTION_KEYWORDS = {
    "title": ["title", "тақырыбы", "тема"],
    "abstract": ["реферат", "abstract", "аннотация"],
    "contents": ["мазмұны", "мазмұн", "содержание", "contents"],
    "introduction": ["кіріспе", "введение", "introduction"],
    "main": ["негізгі", "основн", "chapter", "тарау", "глава"],
    "conclusion": ["қорытынды", "заключение", "conclusion"],
    "references": ["әдебиеттер", "список", "references", "библиография"],
}

STRUCTURAL_HEADINGS = {"мазмұны", "мазмұн", "кіріспе", "қорытынды", "содержание", "введение", "заключение"}

PAGE_THRESHOLDS = {
    "thesis_humanities": 50,
    "thesis_science": 40,
    "project": 40,
}


def _classify_section(heading: str) -> str | None:
    lower = heading.lower()
    for section_type, keywords in SECTION_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return section_type
    return "main"  # Default: treat unknown body sections as main body


class StructureChecker(BaseChecker):
    name = "structure"
    description = "Validates document section order and required sections per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_required_sections(document))
        issues.extend(self._check_section_order(document))
        issues.extend(self._check_structural_headings_not_numbered(document))
        issues.extend(self._check_page_volume(document))
        return issues

    def _check_required_sections(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        found_types = set()
        for section in document.sections:
            classified = _classify_section(section.heading)
            if classified:
                found_types.add(classified)

        required = {"abstract", "contents", "introduction", "conclusion", "references"}
        missing = required - found_types
        for section_type in missing:
            issues.append(Issue(
                severity="error",
                category="structure",
                checker=self.name,
                location=IssueLocation(section_name=section_type),
                message=f"Required section '{section_type}' is missing",
                suggestion=f"Add a '{section_type}' section to your document",
                rule_ref="Sec. 6.4",
            ))
        return issues

    def _check_section_order(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        if not document.sections:
            return issues

        classified_order = []
        for section in document.sections:
            classified = _classify_section(section.heading)
            if classified and classified in REQUIRED_ORDER:
                classified_order.append(classified)

        # Check if the order matches expected
        expected_indices = []
        for section_type in classified_order:
            if section_type in REQUIRED_ORDER:
                expected_indices.append(REQUIRED_ORDER.index(section_type))

        for i in range(1, len(expected_indices)):
            if expected_indices[i] < expected_indices[i - 1]:
                issues.append(Issue(
                    severity="error",
                    category="structure",
                    checker=self.name,
                    location=IssueLocation(section_name=classified_order[i]),
                    message=f"Section '{classified_order[i]}' appears out of order",
                    suggestion=f"Move '{classified_order[i]}' to its correct position per GOST Sec. 6.4",
                    rule_ref="Sec. 6.4",
                ))
        return issues

    def _check_structural_headings_not_numbered(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        number_pattern = re.compile(r"^\d+\s+")
        for para in document.paragraphs:
            if para.is_heading and para.heading_level == 1:
                lower_text = para.text.strip().lower()
                # Check if this is a structural heading
                is_structural = any(sh in lower_text for sh in STRUCTURAL_HEADINGS)
                if is_structural and number_pattern.match(para.text.strip()):
                    issues.append(Issue(
                        severity="warning",
                        category="structure",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=para.paragraph_index,
                            context_text=para.text[:80],
                        ),
                        message=f"Structural heading '{para.text}' should NOT be numbered",
                        suggestion="Remove the number prefix from this structural heading",
                        rule_ref="Sec. 6.4",
                    ))
        return issues

    def _check_page_volume(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        threshold = PAGE_THRESHOLDS.get(document.doc_type, 40)
        if document.page_count_body < threshold:
            issues.append(Issue(
                severity="warning",
                category="structure",
                checker=self.name,
                location=IssueLocation(),
                message=f"Page volume ({document.page_count_body} pages) is below minimum ({threshold} pages) for {document.doc_type}",
                suggestion=f"Add more content to reach at least {threshold} pages (excluding appendices, references, abstract)",
                rule_ref="Sec. 6.2",
            ))
        return issues
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_structure.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/checkers/structure.py backend/tests/test_structure.py
git commit -m "feat: StructureChecker — section order, required sections, page volume"
```

---

## Task 4: FormattingChecker (Dev A)

**Files:**
- Modify: `backend/app/checkers/formatting.py`
- Create: `backend/tests/test_formatting.py`

- [ ] **Step 1: Write FormattingChecker tests**

```python
"""Tests for FormattingChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.formatting import FormattingChecker
from app.parser.structures import DocProperties


class TestFormattingChecker:
    def setup_method(self):
        self.checker = FormattingChecker()

    def test_no_issues_for_correct_formatting(self):
        paragraphs = [
            make_paragraph("Body text", font_name="Times New Roman", font_size=14.0,
                           alignment="justify", line_spacing=1.5, paragraph_index=0),
        ]
        props = DocProperties(
            left_margin_cm=3.0, right_margin_cm=1.0,
            top_margin_cm=2.0, bottom_margin_cm=2.0,
        )
        doc = make_document(paragraphs=paragraphs, properties=props)
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_wrong_font(self):
        paragraphs = [
            make_paragraph("Text", font_name="Arial", font_size=14.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        font_issues = [i for i in issues if "font" in i.message.lower()]
        assert len(font_issues) > 0

    def test_wrong_font_size(self):
        paragraphs = [
            make_paragraph("Text", font_size=12.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        size_issues = [i for i in issues if "size" in i.message.lower() or "14" in i.message]
        assert len(size_issues) > 0

    def test_wrong_margins(self):
        props = DocProperties(
            left_margin_cm=2.0, right_margin_cm=2.0,
            top_margin_cm=2.0, bottom_margin_cm=2.0,
        )
        doc = make_document(properties=props)
        issues = self.checker.check(doc)
        margin_issues = [i for i in issues if "margin" in i.message.lower()]
        assert len(margin_issues) > 0

    def test_wrong_line_spacing(self):
        paragraphs = [
            make_paragraph("Text", line_spacing=1.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        spacing_issues = [i for i in issues if "spacing" in i.message.lower()]
        assert len(spacing_issues) > 0

    def test_heading_not_uppercase(self):
        paragraphs = [
            make_paragraph("кіріспе", is_heading=True, heading_level=1, bold=True,
                           paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        case_issues = [i for i in issues if "uppercase" in i.message.lower() or "capital" in i.message.lower()]
        assert len(case_issues) > 0

    def test_heading_ends_with_period(self):
        paragraphs = [
            make_paragraph("КІРІСПЕ.", is_heading=True, heading_level=1, bold=True,
                           paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        period_issues = [i for i in issues if "period" in i.message.lower()]
        assert len(period_issues) > 0

    def test_text_not_justified(self):
        paragraphs = [
            make_paragraph("Body text", alignment="left", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        align_issues = [i for i in issues if "justif" in i.message.lower() or "alignment" in i.message.lower()]
        assert len(align_issues) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_formatting.py -v`
Expected: FAIL

- [ ] **Step 3: Implement FormattingChecker**

```python
"""FormattingChecker — validates page layout and typography per GOST 7.32-2017 Sec. 6.2."""

from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


EXPECTED_FONT = "Times New Roman"
EXPECTED_FONT_SIZE = 14.0
EXPECTED_LINE_SPACING = 1.5
EXPECTED_MARGINS = {"left": 3.0, "right": 1.0, "top": 2.0, "bottom": 2.0}
MARGIN_TOLERANCE = 0.2  # cm


class FormattingChecker(BaseChecker):
    name = "formatting"
    description = "Validates page layout, typography, and heading styles per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_margins(document))
        issues.extend(self._check_paragraph_formatting(document))
        issues.extend(self._check_heading_style(document))
        return issues

    def _check_margins(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        props = document.properties
        margin_checks = {
            "left": (props.left_margin_cm, EXPECTED_MARGINS["left"]),
            "right": (props.right_margin_cm, EXPECTED_MARGINS["right"]),
            "top": (props.top_margin_cm, EXPECTED_MARGINS["top"]),
            "bottom": (props.bottom_margin_cm, EXPECTED_MARGINS["bottom"]),
        }
        for side, (actual, expected) in margin_checks.items():
            if actual is not None and abs(actual - expected) > MARGIN_TOLERANCE:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(),
                    message=f"{side.capitalize()} margin is {actual:.1f}cm, expected {expected:.1f}cm",
                    suggestion=f"Set {side} margin to {expected:.0f}cm in Page Layout settings",
                    rule_ref="Sec. 6.2",
                ))
        return issues

    def _check_paragraph_formatting(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.text.strip():
                continue

            # Skip headings for font/alignment checks (checked separately)
            if para.is_heading:
                continue

            # Font name
            if para.font_name and para.font_name != EXPECTED_FONT:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Font is '{para.font_name}', expected '{EXPECTED_FONT}'",
                    suggestion=f"Change font to {EXPECTED_FONT}",
                    rule_ref="Sec. 6.2",
                ))

            # Font size
            if para.font_size and abs(para.font_size - EXPECTED_FONT_SIZE) > 0.5:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Font size is {para.font_size}pt, expected {EXPECTED_FONT_SIZE}pt",
                    suggestion=f"Change font size to {EXPECTED_FONT_SIZE}pt",
                    rule_ref="Sec. 6.2",
                ))

            # Line spacing
            if para.line_spacing and abs(para.line_spacing - EXPECTED_LINE_SPACING) > 0.1:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Line spacing is {para.line_spacing}, expected {EXPECTED_LINE_SPACING}",
                    suggestion="Set line spacing to 1.5",
                    rule_ref="Sec. 6.2",
                ))

            # Alignment
            if para.alignment and para.alignment != "justify":
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Text alignment is '{para.alignment}', expected 'justify'",
                    suggestion="Set paragraph alignment to Justify",
                    rule_ref="Sec. 6.2",
                ))

        return issues

    def _check_heading_style(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.is_heading or not para.text.strip():
                continue

            text = para.text.strip()

            # Uppercase check
            if text != text.upper():
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message=f"Heading should be uppercase: '{text}'",
                    suggestion="Convert heading text to UPPERCASE",
                    rule_ref="Sec. 6.2",
                ))

            # No period at end
            if text.endswith("."):
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message="Heading should not end with a period",
                    suggestion="Remove the trailing period from the heading",
                    rule_ref="Sec. 6.2",
                ))

            # Bold check
            if para.bold is False:
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message="Heading should be bold",
                    suggestion="Apply bold formatting to the heading",
                    rule_ref="Sec. 6.2",
                ))

        return issues
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_formatting.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/checkers/formatting.py backend/tests/test_formatting.py
git commit -m "feat: FormattingChecker — margins, font, spacing, heading styles"
```

---

## Task 5: CaptionChecker (Dev B)

**Files:**
- Modify: `backend/app/checkers/captions.py`
- Create: `backend/tests/test_captions.py`

- [ ] **Step 1: Write CaptionChecker tests**

```python
"""Tests for CaptionChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.captions import CaptionChecker
from app.parser.structures import Figure, Table


class TestCaptionChecker:
    def setup_method(self):
        self.checker = CaptionChecker()

    def test_no_issues_for_correct_captions(self):
        figures = [
            Figure(number="1.1", title="Сурет 1.1 - Diagram", paragraph_index=10,
                   has_caption=True, caption_paragraph_index=11, caption_position="below"),
        ]
        tables = [
            Table(number="1.1", title="Кесте 1.1 - Data", paragraph_index=20,
                  has_caption=True, caption_paragraph_index=19, caption_position="above"),
        ]
        doc = make_document(figures=figures, tables=tables)
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_figure_missing_caption(self):
        figures = [
            Figure(number=None, title=None, paragraph_index=10,
                   has_caption=False, caption_paragraph_index=None),
        ]
        doc = make_document(figures=figures)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "missing" in i.message.lower() or "caption" in i.message.lower()]
        assert len(missing) > 0

    def test_figure_caption_above_instead_of_below(self):
        figures = [
            Figure(number="1.1", title="Сурет 1.1", paragraph_index=10,
                   has_caption=True, caption_paragraph_index=9, caption_position="above"),
        ]
        doc = make_document(figures=figures)
        issues = self.checker.check(doc)
        position = [i for i in issues if "below" in i.message.lower() or "position" in i.message.lower()]
        assert len(position) > 0

    def test_table_caption_below_instead_of_above(self):
        tables = [
            Table(number="1.1", title="Кесте 1.1", paragraph_index=20,
                  has_caption=True, caption_paragraph_index=21, caption_position="below"),
        ]
        doc = make_document(tables=tables)
        issues = self.checker.check(doc)
        position = [i for i in issues if "above" in i.message.lower() or "position" in i.message.lower()]
        assert len(position) > 0

    def test_table_missing_caption(self):
        tables = [
            Table(number=None, title=None, paragraph_index=20,
                  has_caption=False, caption_paragraph_index=None),
        ]
        doc = make_document(tables=tables)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "missing" in i.message.lower() or "caption" in i.message.lower()]
        assert len(missing) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_captions.py -v`
Expected: FAIL

- [ ] **Step 3: Implement CaptionChecker**

```python
"""CaptionChecker — validates figure and table captions per GOST 7.32-2017 Sec. 6.5/6.6."""

from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


class CaptionChecker(BaseChecker):
    name = "captions"
    description = "Validates figure and table captions per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_figures(document))
        issues.extend(self._check_tables(document))
        return issues

    def _check_figures(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        prev_number_parts: dict[str, int] = {}  # chapter -> last number

        for fig in document.figures:
            if not fig.has_caption:
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=fig.paragraph_index,
                        context_text="Figure without caption",
                    ),
                    message="Figure is missing a caption",
                    suggestion="Add a caption below the figure in format 'Сурет X.Y — Title'",
                    rule_ref="Sec. 6.5",
                ))
                continue

            if fig.caption_position != "below":
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=fig.caption_paragraph_index,
                        context_text=fig.title or "",
                    ),
                    message="Figure caption must be placed BELOW the figure",
                    suggestion="Move the figure caption to below the figure",
                    rule_ref="Sec. 6.5",
                ))

            # Check sequential numbering
            if fig.number:
                parts = fig.number.split(".")
                if len(parts) == 2:
                    chapter, num = parts[0], int(parts[1]) if parts[1].isdigit() else 0
                    last = prev_number_parts.get(chapter, 0)
                    if num != last + 1 and last > 0:
                        issues.append(Issue(
                            severity="warning",
                            category="captions",
                            checker=self.name,
                            location=IssueLocation(
                                paragraph_index=fig.paragraph_index,
                                context_text=fig.title or "",
                            ),
                            message=f"Figure numbering not sequential: expected {chapter}.{last + 1}, got {fig.number}",
                            suggestion="Ensure figures are numbered sequentially within each chapter",
                            rule_ref="Sec. 6.5",
                        ))
                    prev_number_parts[chapter] = num

        return issues

    def _check_tables(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for table in document.tables:
            if not table.has_caption:
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=table.paragraph_index,
                        context_text="Table without caption",
                    ),
                    message="Table is missing a caption",
                    suggestion="Add a caption above the table in format 'Кесте X.Y — Title'",
                    rule_ref="Sec. 6.6",
                ))
                continue

            if table.caption_position != "above":
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=table.caption_paragraph_index,
                        context_text=table.title or "",
                    ),
                    message="Table caption must be placed ABOVE the table",
                    suggestion="Move the table caption to above the table",
                    rule_ref="Sec. 6.6",
                ))

        return issues
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_captions.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/checkers/captions.py backend/tests/test_captions.py
git commit -m "feat: CaptionChecker — figure/table caption position, numbering"
```

---

## Task 6: SpacingChecker (Dev B)

**Files:**
- Modify: `backend/app/checkers/spacing.py`
- Create: `backend/tests/test_spacing.py`

- [ ] **Step 1: Write SpacingChecker tests**

```python
"""Tests for SpacingChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.spacing import SpacingChecker


class TestSpacingChecker:
    def setup_method(self):
        self.checker = SpacingChecker()

    def test_no_issues_for_clean_text(self):
        paragraphs = [
            make_paragraph("Normal paragraph text.", paragraph_index=0),
            make_paragraph("Another paragraph.", paragraph_index=1),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        assert len(issues) == 0

    def test_trailing_whitespace(self):
        paragraphs = [
            make_paragraph("Text with trailing spaces   ", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        trailing = [i for i in issues if "trailing" in i.message.lower()]
        assert len(trailing) > 0

    def test_multiple_consecutive_spaces(self):
        paragraphs = [
            make_paragraph("Text  with  double  spaces", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        spaces = [i for i in issues if "consecutive" in i.message.lower() or "multiple" in i.message.lower()]
        assert len(spaces) > 0

    def test_wrong_line_spacing(self):
        paragraphs = [
            make_paragraph("Text", line_spacing=2.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        spacing = [i for i in issues if "line spacing" in i.message.lower()]
        assert len(spacing) > 0

    def test_empty_paragraphs_between_sections(self):
        paragraphs = [
            make_paragraph("Section text", paragraph_index=0),
            make_paragraph("", paragraph_index=1),
            make_paragraph("", paragraph_index=2),
            make_paragraph("", paragraph_index=3),
            make_paragraph("Next section", paragraph_index=4),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        blank = [i for i in issues if "blank" in i.message.lower() or "empty" in i.message.lower()]
        assert len(blank) > 0

    def test_tab_characters(self):
        paragraphs = [
            make_paragraph("\tTabbed text", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        tabs = [i for i in issues if "tab" in i.message.lower()]
        assert len(tabs) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_spacing.py -v`
Expected: FAIL

- [ ] **Step 3: Implement SpacingChecker**

```python
"""SpacingChecker — validates whitespace consistency."""

import re
from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


EXPECTED_LINE_SPACING = 1.5
MAX_CONSECUTIVE_BLANK_LINES = 2


class SpacingChecker(BaseChecker):
    name = "spacing"
    description = "Validates whitespace consistency throughout the document"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_trailing_whitespace(document))
        issues.extend(self._check_consecutive_spaces(document))
        issues.extend(self._check_blank_lines(document))
        issues.extend(self._check_line_spacing(document))
        issues.extend(self._check_tabs(document))
        return issues

    def _check_trailing_whitespace(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if para.text and para.text != para.text.rstrip():
                issues.append(Issue(
                    severity="warning",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message="Paragraph has trailing whitespace",
                    suggestion="Remove trailing spaces from the end of the paragraph",
                ))
        return issues

    def _check_consecutive_spaces(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        multi_space = re.compile(r"  +")
        for para in document.paragraphs:
            if para.text and multi_space.search(para.text):
                issues.append(Issue(
                    severity="warning",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message="Multiple consecutive spaces detected",
                    suggestion="Replace multiple spaces with a single space",
                ))
        return issues

    def _check_blank_lines(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        consecutive_blank = 0
        first_blank_index = None
        for para in document.paragraphs:
            if not para.text.strip():
                if consecutive_blank == 0:
                    first_blank_index = para.paragraph_index
                consecutive_blank += 1
            else:
                if consecutive_blank > MAX_CONSECUTIVE_BLANK_LINES:
                    issues.append(Issue(
                        severity="warning",
                        category="spacing",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=first_blank_index,
                            context_text=f"{consecutive_blank} consecutive blank lines",
                        ),
                        message=f"Too many blank lines ({consecutive_blank}) between sections",
                        suggestion=f"Reduce to at most {MAX_CONSECUTIVE_BLANK_LINES} blank lines",
                    ))
                consecutive_blank = 0
                first_blank_index = None
        return issues

    def _check_line_spacing(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.text.strip():
                continue
            if para.line_spacing and abs(para.line_spacing - EXPECTED_LINE_SPACING) > 0.1:
                issues.append(Issue(
                    severity="error",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Line spacing is {para.line_spacing}, expected {EXPECTED_LINE_SPACING}",
                    suggestion="Set line spacing to 1.5 for this paragraph",
                    rule_ref="Sec. 6.2",
                ))
        return issues

    def _check_tabs(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if "\t" in para.text:
                issues.append(Issue(
                    severity="warning",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message="Tab character detected — use paragraph indentation instead",
                    suggestion="Replace tabs with proper paragraph first-line indent (1.0 cm)",
                ))
        return issues
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_spacing.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/checkers/spacing.py backend/tests/test_spacing.py
git commit -m "feat: SpacingChecker — trailing whitespace, consecutive spaces, line spacing, tabs"
```

---

## Task 7: Frontend — React App (Dev B)

**Files:**
- Create: `dissertation-checker/frontend/` (entire React app)

- [ ] **Step 1: Scaffold React + Vite + TypeScript app**

```bash
cd dissertation-checker
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install axios react-dropzone
```

- [ ] **Step 2: Create API client `src/api/client.ts`**

```typescript
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface IssueLocation {
  paragraph_index: number | null;
  page_number: number | null;
  section_name: string | null;
  context_text: string;
}

export interface Issue {
  severity: 'error' | 'warning' | 'info';
  category: string;
  checker: string;
  location: IssueLocation;
  message: string;
  suggestion: string;
  rule_ref: string;
}

export interface Report {
  id: string;
  filename: string;
  checked_at: string;
  doc_type: string;
  total_issues: number;
  issues_by_severity: Record<string, number>;
  issues_by_category: Record<string, number>;
  issues: Issue[];
}

export async function checkDissertation(
  file: File,
  docType: string
): Promise<Report> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('doc_type', docType);
  const response = await axios.post<Report>(`${API_BASE}/check`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getReport(id: string): Promise<Report> {
  const response = await axios.get<Report>(`${API_BASE}/reports/${id}`);
  return response.data;
}
```

- [ ] **Step 3: Create FileUpload component `src/components/FileUpload.tsx`**

```tsx
import { useDropzone } from 'react-dropzone';
import { useCallback } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

export function FileUpload({ onFileSelect, selectedFile }: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) onFileSelect(acceptedFiles[0]);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      style={{
        border: '2px dashed #ccc',
        borderRadius: '8px',
        padding: '40px',
        textAlign: 'center',
        cursor: 'pointer',
        background: isDragActive ? '#f0f0f0' : '#fafafa',
      }}
    >
      <input {...getInputProps()} />
      {selectedFile ? (
        <p>Selected: <strong>{selectedFile.name}</strong></p>
      ) : isDragActive ? (
        <p>Drop the .docx file here...</p>
      ) : (
        <p>Drag & drop a .docx file here, or click to select</p>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create ReportSummary component `src/components/ReportSummary.tsx`**

```tsx
import type { Report } from '../api/client';

interface ReportSummaryProps {
  report: Report;
}

const SEVERITY_COLORS: Record<string, string> = {
  error: '#dc3545',
  warning: '#ffc107',
  info: '#0dcaf0',
};

export function ReportSummary({ report }: ReportSummaryProps) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <h2>Report Summary</h2>
      <p>File: <strong>{report.filename}</strong> | Type: {report.doc_type}</p>
      <p>Total issues: <strong>{report.total_issues}</strong></p>
      <div style={{ display: 'flex', gap: '16px', marginTop: '12px' }}>
        {Object.entries(report.issues_by_severity).map(([severity, count]) => (
          <div
            key={severity}
            style={{
              padding: '12px 20px',
              borderRadius: '8px',
              background: SEVERITY_COLORS[severity] || '#ccc',
              color: severity === 'warning' ? '#000' : '#fff',
            }}
          >
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{count}</div>
            <div>{severity.charAt(0).toUpperCase() + severity.slice(1)}s</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: '12px' }}>
        <h3>By Category</h3>
        <ul>
          {Object.entries(report.issues_by_category).map(([cat, count]) => (
            <li key={cat}>{cat}: {count} issues</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Create IssueCard component `src/components/IssueCard.tsx`**

```tsx
import type { Issue } from '../api/client';

interface IssueCardProps {
  issue: Issue;
}

const SEVERITY_BADGE: Record<string, { bg: string; text: string }> = {
  error: { bg: '#dc3545', text: '#fff' },
  warning: { bg: '#ffc107', text: '#000' },
  info: { bg: '#0dcaf0', text: '#000' },
};

export function IssueCard({ issue }: IssueCardProps) {
  const badge = SEVERITY_BADGE[issue.severity] || { bg: '#ccc', text: '#000' };
  return (
    <div
      style={{
        border: '1px solid #ddd',
        borderRadius: '6px',
        padding: '12px',
        marginBottom: '8px',
      }}
    >
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
        <span
          style={{
            background: badge.bg,
            color: badge.text,
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
          }}
        >
          {issue.severity.toUpperCase()}
        </span>
        <span style={{ background: '#e9ecef', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
          {issue.category}
        </span>
        {issue.rule_ref && (
          <span style={{ fontSize: '12px', color: '#666' }}>{issue.rule_ref}</span>
        )}
      </div>
      <p style={{ margin: '4px 0' }}><strong>{issue.message}</strong></p>
      <p style={{ margin: '4px 0', color: '#555' }}>{issue.suggestion}</p>
      {issue.location.context_text && (
        <p style={{ margin: '4px 0', fontSize: '13px', color: '#888', fontStyle: 'italic' }}>
          Context: "{issue.location.context_text}"
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Create IssueList component `src/components/IssueList.tsx`**

```tsx
import { useState } from 'react';
import type { Issue } from '../api/client';
import { IssueCard } from './IssueCard';

interface IssueListProps {
  issues: Issue[];
}

export function IssueList({ issues }: IssueListProps) {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const categories = [...new Set(issues.map((i) => i.category))];
  const filtered = issues.filter((i) => {
    if (severityFilter !== 'all' && i.severity !== severityFilter) return false;
    if (categoryFilter !== 'all' && i.category !== categoryFilter) return false;
    return true;
  });

  return (
    <div>
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
        <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
          <option value="all">All Severities</option>
          <option value="error">Errors</option>
          <option value="warning">Warnings</option>
          <option value="info">Info</option>
        </select>
        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <span>{filtered.length} of {issues.length} issues shown</span>
      </div>
      {filtered.map((issue, idx) => (
        <IssueCard key={idx} issue={issue} />
      ))}
    </div>
  );
}
```

- [ ] **Step 7: Create UploadPage `src/pages/UploadPage.tsx`**

```tsx
import { useState } from 'react';
import { FileUpload } from '../components/FileUpload';
import { checkDissertation, type Report } from '../api/client';

interface UploadPageProps {
  onReportReady: (report: Report) => void;
}

export function UploadPage({ onReportReady }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('thesis_science');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const report = await checkDissertation(file, docType);
      onReportReady(report);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check document');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', padding: '20px' }}>
      <h1>Dissertation Checker</h1>
      <p>Upload your .docx dissertation to check formatting compliance (GOST 7.32-2017)</p>
      <div style={{ marginBottom: '16px' }}>
        <label>Document Type: </label>
        <select value={docType} onChange={(e) => setDocType(e.target.value)}>
          <option value="thesis_humanities">Thesis (Humanities/Social)</option>
          <option value="thesis_science">Thesis (Natural Science)</option>
          <option value="project">Project</option>
        </select>
      </div>
      <FileUpload onFileSelect={setFile} selectedFile={file} />
      <button
        onClick={handleSubmit}
        disabled={!file || loading}
        style={{
          marginTop: '16px',
          padding: '12px 24px',
          background: '#0d6efd',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          cursor: file && !loading ? 'pointer' : 'not-allowed',
          fontSize: '16px',
        }}
      >
        {loading ? 'Checking...' : 'Check Dissertation'}
      </button>
      {error && <p style={{ color: 'red', marginTop: '12px' }}>{error}</p>}
    </div>
  );
}
```

- [ ] **Step 8: Create ReportPage `src/pages/ReportPage.tsx`**

```tsx
import type { Report } from '../api/client';
import { ReportSummary } from '../components/ReportSummary';
import { IssueList } from '../components/IssueList';

interface ReportPageProps {
  report: Report;
  onBack: () => void;
}

export function ReportPage({ report, onBack }: ReportPageProps) {
  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${report.filename}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ maxWidth: '900px', margin: '40px auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button onClick={onBack} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          ← Check Another
        </button>
        <button onClick={handleDownloadJson} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Download JSON
        </button>
      </div>
      <ReportSummary report={report} />
      <h2>Issues</h2>
      <IssueList issues={report.issues} />
    </div>
  );
}
```

- [ ] **Step 9: Update App.tsx**

```tsx
import { useState } from 'react';
import { UploadPage } from './pages/UploadPage';
import { ReportPage } from './pages/ReportPage';
import type { Report } from './api/client';

function App() {
  const [report, setReport] = useState<Report | null>(null);

  if (report) {
    return <ReportPage report={report} onBack={() => setReport(null)} />;
  }
  return <UploadPage onReportReady={setReport} />;
}

export default App;
```

- [ ] **Step 10: Run frontend dev server and verify**

```bash
cd dissertation-checker/frontend
npm run dev
```

Expected: App loads at `http://localhost:5173`, shows upload page with doc type selector.

- [ ] **Step 11: Commit**

```bash
cd dissertation-checker
git add frontend/
git commit -m "feat: React frontend — upload page, report page with filtering"
```

---

## Task 8: CitationChecker (Dev C)

**Files:**
- Modify: `backend/app/checkers/citations.py`
- Create: `backend/tests/test_citations.py`

- [ ] **Step 1: Write CitationChecker tests**

```python
"""Tests for CitationChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.citations import CitationChecker
from app.parser.structures import Reference


class TestCitationChecker:
    def setup_method(self):
        self.checker = CitationChecker()

    def test_no_issues_for_matching_citations(self):
        paragraphs = [
            make_paragraph("As shown in [1], the method works.", paragraph_index=0),
            make_paragraph("КІРІСПЕ", is_heading=True, heading_level=1, paragraph_index=1),
        ]
        references = [
            Reference(text="[1] Author, Title, Journal, 2024", paragraph_index=50),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_citation_without_reference(self):
        paragraphs = [
            make_paragraph("As shown in [5], the result is clear.", paragraph_index=0),
        ]
        references = [
            Reference(text="[1] Some other reference", paragraph_index=50),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "no matching" in i.message.lower() or "missing" in i.message.lower()]
        assert len(missing) > 0

    def test_reference_not_cited(self):
        paragraphs = [
            make_paragraph("No citations in this text.", paragraph_index=0),
        ]
        references = [
            Reference(text="[1] Author, Title, 2024", paragraph_index=50),
            Reference(text="[2] Another author, 2023", paragraph_index=51),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        uncited = [i for i in issues if "not cited" in i.message.lower() or "unused" in i.message.lower()]
        assert len(uncited) > 0

    def test_references_not_alphabetical(self):
        references = [
            Reference(text="Zhang, A. (2024). Title", paragraph_index=50),
            Reference(text="Adams, B. (2023). Title", paragraph_index=51),
        ]
        paragraphs = [
            make_paragraph("КІРІСПЕ", is_heading=True, heading_level=1, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        order = [i for i in issues if "alphabetical" in i.message.lower() or "order" in i.message.lower()]
        assert len(order) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_citations.py -v`
Expected: FAIL

- [ ] **Step 3: Implement CitationChecker**

```python
"""CitationChecker — validates citation and reference formatting per GOST 7.32-2017 Sec. 6.8."""

import re
from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


# Pattern to match bracket-style citations like [1], [2,3], [1-5]
BRACKET_CITATION = re.compile(r"\[(\d+(?:[,\s\-–]\d+)*)\]")
# Pattern to match author-year citations like (Author, 2024)
AUTHOR_YEAR_CITATION = re.compile(r"\(([A-ZА-Я][a-zа-я]+(?:\s(?:et al|и др)),?\s\d{4})\)")


class CitationChecker(BaseChecker):
    name = "citations"
    description = "Validates citation and reference formatting per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_citation_reference_match(document))
        issues.extend(self._check_reference_order(document))
        return issues

    def _extract_citations(self, document: ParsedDocument) -> dict[int, list[int]]:
        """Extract all bracket-style citations from body text. Returns {paragraph_index: [citation_numbers]}."""
        citations: dict[int, list[int]] = {}
        for para in document.paragraphs:
            if para.is_heading:
                continue
            matches = BRACKET_CITATION.findall(para.text)
            if matches:
                nums = []
                for match in matches:
                    for part in re.split(r"[,\s]", match):
                        part = part.strip().replace("–", "-")
                        if "-" in part:
                            start, end = part.split("-", 1)
                            if start.isdigit() and end.isdigit():
                                nums.extend(range(int(start), int(end) + 1))
                        elif part.isdigit():
                            nums.append(int(part))
                if nums:
                    citations[para.paragraph_index] = nums
        return citations

    def _extract_reference_numbers(self, document: ParsedDocument) -> dict[int, str]:
        """Extract reference numbers from the reference list. Returns {number: reference_text}."""
        refs: dict[int, str] = {}
        ref_num = re.compile(r"^\[(\d+)\]")
        for ref in document.references:
            match = ref_num.match(ref.text.strip())
            if match:
                refs[int(match.group(1))] = ref.text
        return refs

    def _check_citation_reference_match(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        citations = self._extract_citations(document)
        references = self._extract_reference_numbers(document)

        cited_numbers = set()
        for para_idx, nums in citations.items():
            for num in nums:
                cited_numbers.add(num)
                if references and num not in references:
                    para = next(
                        (p for p in document.paragraphs if p.paragraph_index == para_idx), None
                    )
                    issues.append(Issue(
                        severity="error",
                        category="citations",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=para_idx,
                            context_text=para.text[:80] if para else "",
                        ),
                        message=f"Citation [{num}] has no matching reference entry",
                        suggestion=f"Add reference [{num}] to the reference list or remove the citation",
                        rule_ref="Sec. 6.8",
                    ))

        # Check for uncited references
        for ref_num, ref_text in references.items():
            if ref_num not in cited_numbers:
                issues.append(Issue(
                    severity="warning",
                    category="citations",
                    checker=self.name,
                    location=IssueLocation(context_text=ref_text[:80]),
                    message=f"Reference [{ref_num}] is not cited in the text",
                    suggestion="Either cite this reference in the text or remove it from the reference list",
                    rule_ref="Sec. 6.8",
                ))

        return issues

    def _check_reference_order(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        if len(document.references) < 2:
            return issues

        # Check if references use numbered format — if so, alphabetical order doesn't apply
        ref_num = re.compile(r"^\[\d+\]")
        is_numbered = all(ref_num.match(r.text.strip()) for r in document.references[:3] if r.text.strip())

        if not is_numbered:
            # Check alphabetical order for non-numbered references
            for i in range(1, len(document.references)):
                prev = document.references[i - 1].text.strip().lower()
                curr = document.references[i].text.strip().lower()
                if prev and curr and prev > curr:
                    issues.append(Issue(
                        severity="warning",
                        category="citations",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=document.references[i].paragraph_index,
                            context_text=document.references[i].text[:80],
                        ),
                        message="References are not in alphabetical order",
                        suggestion="Sort the reference list alphabetically by author name",
                        rule_ref="Sec. 6.8",
                    ))
                    break  # Report once, not for every pair

        return issues
```

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/test_citations.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/checkers/citations.py backend/tests/test_citations.py
git commit -m "feat: CitationChecker — citation/reference matching, order, uncited refs"
```

---

## Task 9: Integration Tests (Dev C)

**Files:**
- Create: `backend/tests/test_integration.py`

- [ ] **Step 1: Write end-to-end integration test**

```python
"""End-to-end integration tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io


@pytest.fixture
def client():
    return TestClient(app)


def create_sample_docx() -> io.BytesIO:
    """Create a sample .docx with known issues for integration testing."""
    doc = Document()

    # Set correct margins
    section = doc.sections[0]
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(1.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    # Title page
    doc.add_paragraph("ДИССЕРТАЦИЯ")

    # Missing Abstract section (should be flagged)
    # Contents
    doc.add_heading("МАЗМҰНЫ", level=1)
    doc.add_paragraph("1 Кіріспе .......... 3")

    # Introduction
    doc.add_heading("КІРІСПЕ", level=1)
    doc.add_paragraph("This is the introduction text with  double spaces.")

    # Main body
    doc.add_heading("1 НЕГІЗГІ БӨЛІМ", level=1)
    para = doc.add_paragraph("Body text here.")
    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in para.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)

    # Conclusion
    doc.add_heading("ҚОРЫТЫНДЫ", level=1)
    doc.add_paragraph("Conclusion text.")

    # References
    doc.add_heading("ӘДЕБИЕТТЕР ТІЗІМІ", level=1)
    doc.add_paragraph("[1] Author, Title, 2024")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


class TestIntegration:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_check_endpoint_returns_report(self, client):
        docx_file = create_sample_docx()
        response = client.post(
            "/api/check",
            files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"doc_type": "thesis_science"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "issues" in data
        assert data["filename"] == "test.docx"
        assert data["doc_type"] == "thesis_science"
        assert data["total_issues"] > 0

    def test_check_rejects_non_docx(self, client):
        response = client.post(
            "/api/check",
            files={"file": ("test.pdf", b"not a docx", "application/pdf")},
            data={"doc_type": "thesis_science"},
        )
        assert response.status_code == 400

    def test_report_contains_expected_categories(self, client):
        docx_file = create_sample_docx()
        response = client.post(
            "/api/check",
            files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"doc_type": "thesis_science"},
        )
        data = response.json()
        categories = set(data["issues_by_category"].keys())
        # At least structure issues should be present (missing abstract)
        assert "structure" in categories
```

- [ ] **Step 2: Run integration tests**

Run: `cd backend && python -m pytest tests/test_integration.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_integration.py
git commit -m "test: end-to-end integration tests for full pipeline"
```

---

## Task 10: Docker & DevOps (Dev C)

**Files:**
- Create: `dissertation-checker/backend/Dockerfile`
- Create: `dissertation-checker/frontend/Dockerfile`
- Create: `dissertation-checker/docker-compose.yml`

- [ ] **Step 1: Create backend Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create frontend Dockerfile**

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=["http://localhost:5173","http://localhost:80"]

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000/api
```

- [ ] **Step 4: Verify Docker build**

```bash
cd dissertation-checker
docker compose up --build
```

Expected: Backend at `http://localhost:8000`, frontend at `http://localhost:80`

- [ ] **Step 5: Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile docker-compose.yml
git commit -m "infra: Docker setup with docker-compose for backend and frontend"
```

---

## Summary: Final Integration

After all tracks complete:

1. **Dev A** runs: `python -m pytest tests/ -v` — all backend tests pass
2. **Dev B** runs: `npm run build` — frontend builds cleanly
3. **Dev C** runs: `docker compose up` — full stack works end-to-end
4. All developers merge branches, resolve any conflicts in `runner.py` (which imports all checkers)
5. Final commit: `git commit -m "chore: merge all tracks — dissertation checker v1 complete"`
