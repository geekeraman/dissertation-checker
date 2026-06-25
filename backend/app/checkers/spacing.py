"""SpacingChecker — validates whitespace consistency."""

import re
from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


EXPECTED_LINE_SPACING = 1.5
MAX_CONSECUTIVE_BLANK_LINES = 2


class SpacingChecker(BaseChecker):
    name = "spacing"
    description = "Validates whitespace consistency throughout the document"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_trailing_whitespace(document))
        issues.extend(self._check_consecutive_spaces(document))
        issues.extend(self._check_blank_lines(document))
        issues.extend(self._check_line_spacing(document))
        issues.extend(self._check_tabs(document))
        return issues

    def _check_trailing_whitespace(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if para.text and para.text != para.text.rstrip():
                issues.append(Issue(
                    severity="warning",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message="Paragraph has trailing whitespace",
                    suggestion="Remove trailing spaces from the end of the paragraph",
                ))
        return issues

    def _check_consecutive_spaces(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        multi_space = re.compile(r"  +")
        for para in document.paragraphs:
            if para.text and multi_space.search(para.text):
                issues.append(Issue(
                    severity="warning",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message="Multiple consecutive spaces detected",
                    suggestion="Replace multiple spaces with a single space",
                ))
        return issues

    def _check_blank_lines(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        consecutive_blank = 0
        first_blank_index = None
        for para in document.paragraphs:
            if not para.text.strip():
                if consecutive_blank == 0:
                    first_blank_index = para.paragraph_index
                consecutive_blank += 1
            else:
                if consecutive_blank > MAX_CONSECUTIVE_BLANK_LINES:
                    issues.append(Issue(
                        severity="warning",
                        category="spacing",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=first_blank_index,
                            context_text=f"{consecutive_blank} consecutive blank lines",
                        ),
                        message=f"Too many blank lines ({consecutive_blank}) between sections",
                        suggestion=f"Reduce to at most {MAX_CONSECUTIVE_BLANK_LINES} blank lines",
                    ))
                consecutive_blank = 0
                first_blank_index = None
        # Check for trailing blank lines at end of document
        if consecutive_blank > MAX_CONSECUTIVE_BLANK_LINES:
            issues.append(Issue(
                severity="warning",
                category="spacing",
                checker=self.name,
                location=IssueLocation(
                    paragraph_index=first_blank_index,
                    context_text=f"{consecutive_blank} consecutive blank lines",
                ),
                message=f"Too many blank lines ({consecutive_blank}) at end of document",
                suggestion=f"Reduce to at most {MAX_CONSECUTIVE_BLANK_LINES} blank lines",
            ))
        return issues

    def _check_line_spacing(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.text.strip():
                continue
            if para.line_spacing and abs(para.line_spacing - EXPECTED_LINE_SPACING) > 0.1:
                issues.append(Issue(
                    severity="error",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Line spacing is {para.line_spacing}, expected {EXPECTED_LINE_SPACING}",
                    suggestion="Set line spacing to 1.5 for this paragraph",
                    rule_ref="Sec. 6.2",
                ))
        return issues

    def _check_tabs(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if "\t" in para.text:
                issues.append(Issue(
                    severity="warning",
                    category="spacing",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message="Tab character detected — use paragraph indentation instead",
                    suggestion="Replace tabs with proper paragraph first-line indent (1.0 cm)",
                ))
        return issues
