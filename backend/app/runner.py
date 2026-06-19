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
