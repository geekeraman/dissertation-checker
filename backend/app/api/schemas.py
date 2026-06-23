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
