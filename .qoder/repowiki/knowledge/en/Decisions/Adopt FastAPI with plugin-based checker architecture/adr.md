# Adopt FastAPI with plugin-based checker architecture

_Source: coding plans from commit period 6fcc7b3 → 7c95201 — records intent at planning time; the implementation may lag or differ._

**Status:** accepted

## Context
The project requires a backend service to validate academic dissertations against multiple independent rules (captions, spacing, structure, etc.) while exposing a simple API for a React frontend. The system needs to be extensible to add new validation rules without modifying the core orchestration logic.

## Decision drivers
- Extensibility for new validation rules
- Separation of parsing, validation, and API concerns
- Type safety via Pydantic models

## Considered options
- **FastAPI with BaseChecker interface and CheckerRunner** — pros: Enforces a standard contract for all checkers via `BaseChecker`; `CheckerRunner` orchestrates execution independently of specific rules; Pydantic ensures strict data validation for API schemas and domain models (`Issue`, `Report`).; cons: Requires initial scaffolding of abstract base classes and runner logic before implementing specific checkers.
- **Monolithic script or framework-less approach** _(rejected)_ — pros: Faster initial setup for a single rule.; cons: Hard to maintain as validation rules grow; mixing of parsing, business logic, and HTTP handling leads to tight coupling.

## Decision
Implement the backend using FastAPI, structured with a `BaseChecker` abstract interface in `backend/app/checkers/base.py`. A `CheckerRunner` in `backend/app/runner.py` will dynamically execute all registered checkers. Domain models (`Issue`, `Report`) and API schemas are defined using Pydantic in `backend/app/core/models.py` and `backend/app/api/schemas.py` respectively.

## Consequences
New validation rules can be added by simply creating a new class implementing `BaseChecker` and registering it, without touching the API layer or other checkers. The `CheckerRunner` becomes a critical dependency for testability and execution order management.