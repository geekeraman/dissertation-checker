"""SpacingChecker — stub, implemented by Dev B in Task 6."""

from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument


class SpacingChecker(BaseChecker):
    name = "spacing"
    description = "Validates whitespace consistency"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 6
