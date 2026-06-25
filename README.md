# Dissertation Checker

A web service that checks student dissertations (.docx) for formatting issues based on **GOST 7.32-2017** (Kazakhstani university standard). Students upload their document and get a detailed compliance report.

**Status:** v1 — All 5 checkers implemented and tested. Supports Kazakh, Russian, and English documents.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| Doc Parsing | python-docx |
| Frontend | React 18, Vite, TypeScript |
| Containerization | Docker, docker-compose |

## How to Run

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload --port 8000

# Run tests
python -m pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (full stack)

```bash
docker-compose up --build
```

The frontend will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

---

## GOST 7.32-2017 Requirements Coverage

### Formatting (FormattingChecker)
| # | Requirement | Status | Rule |
|---|---|---|---|
| 1 | Font: Times New Roman | ✅ Checked | Sec. 6.2 |
| 2 | Font size: 14pt | ✅ Checked | Sec. 6.2 |
| 3 | Line spacing: 1.5 | ✅ Checked | Sec. 6.2 |
| 4 | Margins: Left 30mm, Right 10mm, Top/Bottom 20mm | ✅ Checked | Sec. 6.2 |
| 5 | Text alignment: Justified | ✅ Checked | Sec. 6.2 |
| 6 | Headings: Uppercase | ✅ Checked | Sec. 6.2 |
| 7 | Headings: Bold | ✅ Checked | Sec. 6.2 |
| 8 | Headings: Centered | ✅ Checked | Sec. 6.2 |
| 9 | Headings: No trailing period | ✅ Checked | Sec. 6.2 |
| 10 | Paragraph first-line indent: 1.25cm | ✅ Checked | Sec. 6.2 |
| 11 | Page numbering (advisory) | ℹ️ Advisory | Sec. 6.2 |

### Document Structure (StructureChecker)
| # | Requirement | Status | Rule |
|---|---|---|---|
| 12 | Required sections present | ✅ Checked | Sec. 6.4 |
| 13 | Section order (GOST standard) | ✅ Checked | Sec. 6.4 |
| 14 | Page volume thresholds | ✅ Checked | Sec. 6.4 |
| 15 | Structural headings not numbered | ✅ Checked | Sec. 6.4 |
| 16 | Major sections start on new page | ✅ Checked | Sec. 6.4 |
| 17 | Abstract word count (advisory) | ℹ️ Advisory | Sec. 6.4 |

### Captions (CaptionChecker)
| # | Requirement | Status | Rule |
|---|---|---|---|
| 18 | Figure captions present | ✅ Checked | Sec. 6.5 |
| 19 | Figure captions below figure | ✅ Checked | Sec. 6.5 |
| 20 | Figure sequential numbering | ✅ Checked | Sec. 6.5 |
| 21 | Figure caption format (Сурет/Рисунок/Figure prefix) | ✅ Checked | Sec. 6.5 |
| 22 | Table captions present | ✅ Checked | Sec. 6.6 |
| 23 | Table captions above table | ✅ Checked | Sec. 6.6 |
| 24 | Table caption format (Кесте/Таблица/Table prefix) | ✅ Checked | Sec. 6.6 |

### Spacing (SpacingChecker)
| # | Requirement | Status | Rule |
|---|---|---|---|
| 25 | No trailing whitespace | ✅ Checked | Sec. 6.2 |
| 26 | No multiple consecutive spaces | ✅ Checked | Sec. 6.2 |
| 27 | No excessive blank lines | ✅ Checked | Sec. 6.2 |
| 28 | No tab characters | ✅ Checked | Sec. 6.2 |

### Citations (CitationChecker)
| # | Requirement | Status | Rule |
|---|---|---|---|
| 29 | Every citation has matching reference | ✅ Checked | Sec. 6.8 |
| 30 | Every reference is cited in text | ✅ Checked | Sec. 6.8 |
| 31 | Reference list alphabetical order | ✅ Checked | Sec. 6.8 |
| 32 | Citation style consistency | ✅ Checked | Sec. 6.8 |

### Language Support
- ✅ Kazakh (primary): АҢДАТПА, МАЗМҰНЫ, КІРІСПЕ, ҚОРЫТЫНДЫ, etc.
- ✅ Russian: РЕФЕРАТ, СОДЕРЖАНИЕ, ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ, etc.
- ✅ English: ABSTRACT, CONTENTS, INTRODUCTION, CONCLUSION, etc.

**Total: 32 requirements checked** (28 validated + 2 advisory + 2 info-level)

---

## Project Structure

```
dissertation-checker/
├── README.md              ← You are here
├── docs/
│   ├── design.md          ← WHAT we're building
│   └── plan.md            ← HOW to build it (tasks with code)
├── backend/
│   ├── app/
│   │   ├── api/           ← API endpoints
│   │   ├── core/          ← Config, models (shared)
│   │   ├── parser/        ← DOCX parsing (shared)
│   │   ├── checkers/      ← Independent checker plugins
│   │   ├── runner.py      ← Orchestrates all checkers
│   │   └── main.py        ← FastAPI app entry
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/    ← React components
│   │   ├── pages/         ← Upload + Report pages
│   │   └── api/           ← API client
│   └── package.json
└── docker-compose.yml
```

---

## Team Assignments

### Developer A — Core + Structure + Formatting
- DOCX Parser
- StructureChecker (section order, required sections)
- FormattingChecker (margins, fonts, heading styles)

### Developer B — Captions + Spacing + Frontend
- CaptionChecker (figure/table captions)
- SpacingChecker (whitespace, line spacing)
- Frontend (React upload + report pages)

### Developer C — Citations + Integration + DevOps
- CitationChecker (citations ↔ references)
- Integration Tests (end-to-end)
- Docker & DevOps

---

## Git Workflow

```bash
# 1. Create your branch
git checkout -b dev-a/structure-formatting      # Dev A
git checkout -b dev-b/captions-spacing-frontend # Dev B
git checkout -b dev-c/citations-docker          # Dev C

# 2. Work on your tasks, commit after each one
git add -A
git commit -m "feat: describe what you built"
git push origin YOUR_BRANCH_NAME

# 3. When done, create a Pull Request on GitHub
# 4. After merge, everyone pulls the latest
git checkout main
git pull origin main
```

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```
# Dissertation Checker

A web service that checks student dissertations (.docx) for formatting issues based on **GOST 7.32-2017** (Kazakhstani university standard). Students upload their document and get a detailed compliance report.

## Quick Start for Team Members

> **First time here?** Read this section, then check your assignment below.

### 1. Clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/dissertation-checker.git
cd dissertation-checker
```

### 2. Read the docs (in this order)

| # | Document | What it tells you | Time to read |
|---|----------|-------------------|--------------|
| 1 | [docs/design.md](docs/design.md) | **WHAT** we're building — architecture, GOST rules, checker specs | 15 min |
| 2 | [docs/plan.md](docs/plan.md) | **HOW** to build it — step-by-step tasks with code | Your assigned tasks |

### 3. Set up your environment

```bash
# Install Python 3.11+ (check: python3 --version)
# Install Node.js 18+ (check: node --version)

# Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Frontend setup (in a separate terminal)
cd frontend
npm install
```

### 4. Find your assignment

---

## Team Assignments

### Developer A — Core + Structure + Formatting

**You build:** The foundation everyone depends on, plus 2 checkers.

**Your tasks in [docs/plan.md](docs/plan.md):**
- Task 1: Shared Foundation (Day 1, with everyone)
- Task 2: DOCX Parser
- Task 3: StructureChecker (section order, required sections)
- Task 4: FormattingChecker (margins, fonts, heading styles)

**Your files:**
```
backend/app/core/models.py
backend/app/core/config.py
backend/app/parser/structures.py
backend/app/parser/docx_parser.py
backend/app/checkers/base.py
backend/app/checkers/structure.py
backend/app/checkers/formatting.py
backend/app/runner.py
backend/app/main.py
backend/app/api/routes.py
backend/app/api/schemas.py
```

**To start:** Open Qoder and say:
> "Execute Task 2 from docs/plan.md"

---

### Developer B — Captions + Spacing + Frontend

**You build:** 2 checkers and the entire student-facing website.

**Your tasks in [docs/plan.md](docs/plan.md):**
- Task 1: Shared Foundation (Day 1, with everyone)
- Task 5: CaptionChecker (figure/table captions)
- Task 6: SpacingChecker (whitespace, line spacing)
- Task 7: Frontend (React upload + report pages)

**Your files:**
```
backend/app/checkers/captions.py
backend/app/checkers/spacing.py
frontend/  (entire folder)
```

**To start:** Open Qoder and say:
> "Execute Task 5 from docs/plan.md"

---

### Developer C — Citations + Integration + DevOps

**You build:** 1 checker, integration tests, and Docker packaging.

**Your tasks in [docs/plan.md](docs/plan.md):**
- Task 1: Shared Foundation (Day 1, with everyone)
- Task 8: CitationChecker (citations ↔ references)
- Task 9: Integration Tests (end-to-end)
- Task 10: Docker & DevOps

**Your files:**
```
backend/app/checkers/citations.py
backend/tests/test_integration.py
backend/Dockerfile
frontend/Dockerfile
docker-compose.yml
```

**To start:** Open Qoder and say:
> "Execute Task 8 from docs/plan.md"

---

## Git Workflow (Simplified)

```bash
# 1. Create your branch (Day 1, after Task 1 is merged)
git checkout -b dev-a/structure-formatting      # Dev A
git checkout -b dev-b/captions-spacing-frontend # Dev B
git checkout -b dev-c/citations-docker          # Dev C

# 2. Work on your tasks, commit after each one
git add -A
git commit -m "feat: describe what you built"
git push origin YOUR_BRANCH_NAME

# 3. When done, create a Pull Request on GitHub
# 4. After merge, everyone pulls the latest
git checkout main
git pull origin main
```

## Daily Standup Template

Post this in your team chat every day:

```
Daily Update
Finished: Task X — [name]
Working on: Task Y — [name]
Blocked: [nothing / describe problem]
```

## Golden Rules

1. **Never edit someone else's file** without asking them first
2. **Push to GitHub every day** — don't lose your work
3. **Run tests before committing**: `python -m pytest tests/ -v`
4. **Stuck for 30+ minutes?** Ask the team or ask Qoder to debug
5. **One task at a time** — don't rush ahead

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| Doc Parsing | python-docx |
| Frontend | React 18, Vite, TypeScript |
| Containerization | Docker, docker-compose |

## Project Structure

```
dissertation-checker/
├── README.md              ← You are here
├── docs/
│   ├── design.md          ← WHAT we're building
│   └── plan.md            ← HOW to build it (tasks with code)
├── backend/
│   ├── app/
│   │   ├── api/           ← API endpoints
│   │   ├── core/          ← Config, models (shared)
│   │   ├── parser/        ← DOCX parsing (shared)
│   │   ├── checkers/      ← Independent checker plugins
│   │   ├── runner.py      ← Orchestrates all checkers
│   │   └── main.py        ← FastAPI app entry
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/    ← React components
│   │   ├── pages/         ← Upload + Report pages
│   │   └── api/           ← API client
│   └── package.json
└── docker-compose.yml
```
