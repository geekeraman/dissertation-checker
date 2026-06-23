"""Base checker interface for all dissertation checkers."""

from abc import ABC, abstractmethod

from app.core.models import Issue
from app.parser.structures import ParsedDocument


class BaseChecker(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def check(self, document: ParsedDocument) -> list[Issue]:
        """Run checks against the parsed document and return issues found."""
        ...
