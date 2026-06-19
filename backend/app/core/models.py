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
