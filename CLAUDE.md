# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Web service that validates Kazakhstani university dissertations (`.docx`) against **GOST 7.32-2017**. Backend parses the document and runs independent checker plugins; frontend lets a student upload a file and renders the resulting issue report. Documents may be in **Kazakh, Russian, or English** — all checkers and the parser must handle all three.

`docs/design.md` describes the rules being enforced; `docs/plan.md` is the original per-task build plan.

## Common commands

Backend (run from `backend/`, with `.venv` activated):

```bash
pip install -e ".[dev]"                       # install + dev deps
uvicorn app.main:app --reload --port 8000     # dev server
python -m pytest tests/ -v                    # all tests
python -m pytest tests/test_structure.py -v   # one test file
python -m pytest tests/test_structure.py::test_name -v   # one test
ruff check .                                  # lint (line-length 100, py311)
```

Frontend (run from `frontend/`):

```bash
npm install
npm run dev        # Vite dev server on :5173
npm run build      # tsc -b && vite build (type-checks before bundling)
npm run lint       # eslint
```

Full stack:

```bash
docker-compose up --build    # frontend on :80, backend on :8000
```

## Architecture

### Pipeline (one request)

`POST /api/check` (`backend/app/api/routes.py`) →
`parse_docx(path, doc_type)` (`backend/app/parser/docx_parser.py`) returns a `ParsedDocument` →
`CheckerRunner.run(document, filename)` (`backend/app/runner.py`) calls every registered `BaseChecker` →
each checker returns a `list[Issue]` → aggregated into a `Report` (counts grouped by severity and category) → returned as JSON.

The runner is intentionally dumb: checkers are **independent plugins** that only read `ParsedDocument` and only emit `Issue`s. They do not share state. Adding a checker = subclass `BaseChecker` in `backend/app/checkers/base.py`, implement `check(document) -> list[Issue]`, and `runner.register(...)` it in `create_runner()` in `routes.py`.

### Single source of truth: `ParsedDocument`

All parsing complexity lives in `backend/app/parser/docx_parser.py`; checkers never touch python-docx directly. The schema is in `backend/app/parser/structures.py` — `ParsedParagraph` (font/size/alignment/spacing/indent/page-break-before), `DocumentSection`, `Figure`, `Table`, `Reference`, `DocProperties` (margins, default font). When a checker needs new data, add a field to `ParsedDocument` and populate it in the parser rather than re-parsing inside the checker.

### `Issue` and `Report` shape

Defined in `backend/app/core/models.py` and mirrored in `frontend/src/api/client.ts`. Every `Issue` carries `severity` (`error`/`warning`/`info`), `category`, `checker`, `IssueLocation` (paragraph index, page, section, context snippet), human `message`, `suggestion`, and a `rule_ref` like `"GOST 7.32-2017 Sec. 6.2"`. **If you change `Issue` or `Report` in Python, update the TypeScript interfaces in `client.ts` to match** — the frontend deserializes by structural shape, not a generated client.

### Document type

`doc_type` (`thesis_humanities` | `thesis_science` | `project`) is supplied by the upload form and drives type-specific rules (e.g. `PAGE_THRESHOLDS` in `structure.py`). It is carried on `ParsedDocument.doc_type` and `Report.doc_type`.

### Trilingual matching

Section/heading recognition uses keyword tables (e.g. `SECTION_KEYWORDS`, `STRUCTURAL_HEADINGS` in `structure.py`; `_STRUCTURAL_HEADING_KEYWORDS` in `docx_parser.py`) that list Kazakh, Russian, and English variants side by side. When adding a new structural concept, add **all three languages** in the same place; do not scatter language variants across checkers. Caption prefixes follow the same pattern (`Сурет`/`Рисунок`/`Figure`, `Кесте`/`Таблица`/`Table`).

### Frontend

Vite + React 18 + TypeScript. Two pages (`UploadPage`, `ReportPage`) drive the whole flow; `src/api/client.ts` is the only network layer. `VITE_API_URL` overrides the API base (set by `docker-compose.yml` to `http://localhost:8000/api`).

## Testing conventions

Checker tests are unit tests built on `make_document` / `make_paragraph` fixtures in `backend/tests/conftest.py` — they construct a `ParsedDocument` directly rather than parsing a real `.docx`, so the parser is decoupled from checker tests. `test_parser.py` and `test_integration.py` exercise real fixtures. Prefer the fixture helpers when adding checker tests; only reach for a real `.docx` when verifying parser behavior or end-to-end flow.
