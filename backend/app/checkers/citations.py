"""CitationChecker — stub, implemented by Dev C in Task 8."""

from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument


class CitationChecker(BaseChecker):
    name = "citations"
    description = "Validates citation and reference formatting"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 8
