"""CaptionChecker — stub, implemented by Dev B in Task 5."""

from app.checkers.base import BaseChecker
from app.core.models import Issue
from app.parser.structures import ParsedDocument


class CaptionChecker(BaseChecker):
    name = "captions"
    description = "Validates figure and table captions"

    def check(self, document: ParsedDocument) -> list[Issue]:
        return []  # Implemented in Task 5
