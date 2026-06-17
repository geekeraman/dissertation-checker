# Dissertation Checking and Normalization Service — Design Spec

**Date:** 2026-06-16
**Status:** Approved
**Standard:** GOST 7.32-2017 (Kazakhstani university standard)
**Team:** 2-3 developers using Qoder

## Overview

A web-based service that allows students to upload their dissertation Word documents (.docx) and receive a detailed formatting compliance report. The service checks documents against the GOST 7.32-2017 university formatting standard and highlights all issues with severity levels and actionable suggestions.

**v1 scope:** Report-only (no auto-fix).

## Architecture

**Plugin-Based Checker Architecture** with independent checker modules implementing a common interface.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| Doc Parsing | python-docx, docx.opc |
| Frontend | React 18, Vite, TypeScript |
| API Communication | REST JSON |
| Containerization | Docker, docker-compose |

### Project Structure

```
dissertation-checker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── api/
│   │   │   ├── routes.py        # API endpoints
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   ├── core/
│   │   │   ├── config.py        # App configuration
│   │   │   └── models.py        # Domain models (Issue, Report, etc.)
│   │   ├── parser/
│   │   │   ├── docx_parser.py   # Main DOCX parsing logic
│   │   │   └── structures.py    # ParsedDocument data structures
│   │   ├── checkers/
│   │   │   ├── base.py          # BaseChecker abstract interface
│   │   │   ├── structure.py     # StructureChecker
│   │   │   ├── formatting.py    # FormattingChecker
│   │   │   ├── captions.py      # CaptionChecker
│   │   │   ├── spacing.py       # SpacingChecker
│   │   │   └── citations.py     # CitationChecker
│   │   └── runner.py            # Orchestrates all checkers
│   ├── tests/
│   │   ├── fixtures/            # Sample .docx test files
│   │   ├── test_structure.py
│   │   ├── test_formatting.py
│   │   ├── test_captions.py
│   │   ├── test_spacing.py
│   │   ├── test_citations.py
│   │   └── test_runner.py
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── ReportSummary.tsx
│   │   │   ├── IssueList.tsx
│   │   │   └── IssueCard.tsx
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx
│   │   │   └── ReportPage.tsx
│   │   ├── api/
│   │   │   └── client.ts        # API client
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Data Flow

```
Student uploads .docx
    → API receives file, saves temporarily
    → Parser extracts ParsedDocument (paragraphs, styles, figures, tables, sections)
    → Runner executes all 5 checkers sequentially
    → Each checker returns list[Issue]
    → Runner aggregates into Report
    → API returns Report JSON
    → Frontend renders visual report
    → Temp file deleted
```

## Shared Contracts

### BaseChecker Interface

```python
from abc import ABC, abstractmethod

class BaseChecker(ABC):
    name: str
    description: str

    @abstractmethod
    def check(self, document: ParsedDocument) -> list[Issue]:
        """Run checks and return a list of issues found."""
        ...
```

### Issue Model

```python
@dataclass
class Issue:
    severity: Literal["error", "warning", "info"]
    category: str           # e.g., "structure", "formatting", "captions"
    checker: str            # checker name that produced this
    location: IssueLocation # paragraph index, page number, section name
    message: str            # human-readable description
    suggestion: str         # how to fix it
    rule_ref: str           # reference to GOST section (e.g., "Sec. 6.4")
```

### IssueLocation

```python
@dataclass
class IssueLocation:
    paragraph_index: int | None
    page_number: int | None
    section_name: str | None
    context_text: str       # snippet of surrounding text for display
```

### Report Model

```python
@dataclass
class Report:
    id: str
    filename: str
    checked_at: datetime
    total_issues: int
    issues_by_severity: dict[str, int]   # {"error": 5, "warning": 12, "info": 3}
    issues_by_category: dict[str, int]   # {"structure": 3, "formatting": 8, ...}
    issues: list[Issue]
```

### ParsedDocument

```python
@dataclass
class ParsedDocument:
    doc_type: str  # "thesis_humanities" | "thesis_science" | "project"
    paragraphs: list[ParsedParagraph]
    sections: list[DocumentSection]
    figures: list[Figure]
    tables: list[Table]
    references: list[Reference]
    metadata: DocumentMetadata
    page_count: int
    page_count_body: int  # excluding appendices, references, abstract
    properties: DocProperties  # margins, default font, line spacing
```

### API Contract

```
POST /api/check
  Request: multipart/form-data with:
    - file: .docx document
    - doc_type: "thesis_humanities" | "thesis_science" | "project"
      (determines page volume thresholds)
  Response: 200 Report JSON
            400 Invalid file format
            422 Parsing error

GET /api/reports/{id}
  Response: 200 Report JSON
            404 Not found

GET /api/health
  Response: 200 {"status": "ok"}
```

## Checker Specifications

### 1. StructureChecker

Validates document section order and required sections per GOST 7.32-2017 Sec. 6.4.

| Check | Severity | Rule Reference |
|-------|----------|---------------|
| Required section order: Title → Abstract → Contents → Introduction → Main body → Conclusion → References → Appendices | Error | Sec. 6.4 |
| Required headings present: МАЗМҰНЫ, КІРІСПЕ, ҚОРЫТЫНДЫ, reference list | Error | Sec. 6.4 |
| Structural headings (МАЗМҰНЫ, КІРІСПЕ, ҚОРЫТЫНДЫ) are NOT numbered | Warning | Sec. 6.4 |
| Each major section starts on a new page | Warning | Sec. 6.4 |
| Sub-sections continue on same page (no unnecessary page breaks) | Info | Sec. 6.4 |
| Page volume: thesis ≥ 50 pages (humanities) / ≥ 40 pages (science) | Warning | Sec. 6.2 |
| Page volume: project ≥ 40 pages | Warning | Sec. 6.2 |
| Page count excludes appendices, references, abstract | Info | Sec. 6.2 |

### 2. FormattingChecker

Validates page layout, typography, and heading styles per GOST 7.32-2017.

| Check | Severity | Rule Reference |
|-------|----------|---------------|
| Font: Times New Roman | Error | Sec. 6.2 |
| Font size: 14pt body text | Error | Sec. 6.2 |
| Line spacing: 1.5 | Error | Sec. 6.2 |
| Margins: left 30mm, right 10mm, top 20mm, bottom 20mm | Error | Sec. 6.2 |
| Text alignment: justified | Warning | Sec. 6.2 |
| Page numbers: Arabic numerals, bottom-center | Error | Sec. 6.2 |
| Title page counts as page 1 but number hidden | Warning | Sec. 6.2 |
| Headings: uppercase, centered, bold | Warning | Sec. 6.2 |
| Headings: no period at end | Warning | Sec. 6.2 |
| Headings: no hyphenation | Warning | Sec. 6.2 |
| Abstract: approximately 1,000 words | Info | Appendix 2 |

### 3. CaptionChecker

Validates figure and table captions per GOST 7.32-2017.

| Check | Severity | Rule Reference |
|-------|----------|---------------|
| Figure numbering: Arabic numerals (e.g., "Сурет 1.1") | Error | Sec. 6.5 |
| Figure caption placed below figure, centered | Error | Sec. 6.5 |
| Figure placed after first mention in text | Warning | Sec. 6.5 |
| Figure has: number, title, image, legend if needed | Warning | Sec. 6.5 |
| Sequential numbering within chapters | Warning | Sec. 6.5 |
| Table numbering: Arabic numerals | Error | Sec. 6.6 |
| Table caption placed above table | Error | Sec. 6.6 |
| Table placed after first mention in text | Warning | Sec. 6.6 |
| Missing captions for detected figures/tables | Error | — |

### 4. SpacingChecker

Validates whitespace consistency throughout the document.

| Check | Severity | Rule Reference |
|-------|----------|---------------|
| Trailing whitespace in paragraphs | Warning | — |
| Leading whitespace in paragraphs (unintended indentation) | Warning | — |
| Multiple consecutive spaces | Warning | — |
| Extra blank lines between sections | Warning | — |
| Line spacing inconsistency (must be 1.5 throughout) | Error | Sec. 6.2 |
| Tab vs space inconsistencies | Warning | — |

### 5. CitationChecker

Validates citation and reference formatting.

| Check | Severity | Rule Reference |
|-------|----------|---------------|
| In-text citation format consistency | Warning | Sec. 6.8 |
| Every in-text citation has matching reference entry | Error | Sec. 6.8 |
| Every reference entry is cited at least once | Warning | Sec. 6.8 |
| Reference list: alphabetical order | Warning | Sec. 6.8 |
| Reference list: consistent formatting style | Warning | Sec. 6.8 |

## Frontend Design

### Upload Page
- Document type selector (thesis humanities / thesis science / project)
- Drag-and-drop zone for `.docx` files
- File type validation (client-side)
- Upload progress indicator
- "Check Dissertation" button

### Report Page
- **Summary dashboard:** Total issues, breakdown by severity (error/warning/info) with color coding, breakdown by category
- **Filterable issue list:** Filter by severity, filter by category, sort by location in document
- **Issue cards:** Show severity badge, category tag, location (page/paragraph), message, suggestion, GOST rule reference, context text snippet
- **Navigation:** Back to upload, download report as JSON

## Team Work Split

### Developer A — Core + Structure + Formatting
- Project scaffolding (FastAPI app, shared models, BaseChecker, runner)
- `StructureChecker` implementation + tests
- `FormattingChecker` implementation + tests
- `docx_parser.py` and `structures.py` (shared parsing layer)
- Test fixtures (sample .docx files with known issues)

### Developer B — Captions + Spacing + Frontend
- `CaptionChecker` implementation + tests
- `SpacingChecker` implementation + tests
- Frontend: React/Vite scaffolding
- Upload page + Report page (summary dashboard, issue list, issue cards)
- API client integration

### Developer C — Citations + Integration + DevOps
- `CitationChecker` implementation + tests
- End-to-end integration tests (upload → full report)
- Docker + docker-compose setup
- CI/CD pipeline
- Frontend polish: responsive design, accessibility

### Day 1 Shared Tasks
- Agree on and commit shared contracts (models, interfaces, API schemas)
- Set up project repository
- Create test fixture .docx files

## Non-Functional Requirements

- Max upload file size: 50 MB
- Check processing time: < 30 seconds for a 100-page document
- Temporary file cleanup after processing
- No persistent storage of uploaded documents (privacy)
- API rate limiting: 10 requests/minute per IP
- CORS configured for frontend origin

## Future Considerations (Out of v1 Scope)

- Auto-fix mode: automatically fix detected issues and return corrected .docx
- Multi-standard support: configurable rules for different universities
- PDF input support
- User accounts and report history
- Batch processing for departments
- LLM-assisted content quality checks (grammar, coherence)
