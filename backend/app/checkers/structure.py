"""StructureChecker — validates document section order per GOST 7.32-2017 Sec. 6.4."""

import re
from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


REQUIRED_ORDER = [
    "title",
    "abstract",
    "contents",
    "introduction",
    "main",
    "conclusion",
    "references",
]

# Keywords for matching section headings (Kazakh + Russian variants)
SECTION_KEYWORDS = {
    "title": ["title", "тақырыбы", "тема"],
    "abstract": ["реферат", "abstract", "аннотация"],
    "contents": ["мазмұны", "мазмұн", "содержание", "contents"],
    "introduction": ["кіріспе", "введение", "introduction"],
    "main": ["негізгі", "основн", "chapter", "тарау", "глава"],
    "conclusion": ["қорытынды", "заключение", "conclusion"],
    "references": ["әдебиеттер", "список", "references", "библиография"],
}

STRUCTURAL_HEADINGS = {"мазмұны", "мазмұн", "кіріспе", "қорытынды", "содержание", "введение", "заключение"}

PAGE_THRESHOLDS = {
    "thesis_humanities": 50,
    "thesis_science": 40,
    "project": 40,
}


def _classify_section(heading: str) -> str | None:
    lower = heading.lower()
    for section_type, keywords in SECTION_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return section_type
    return "main"  # Default: treat unknown body sections as main body


class StructureChecker(BaseChecker):
    name = "structure"
    description = "Validates document section order and required sections per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_required_sections(document))
        issues.extend(self._check_section_order(document))
        issues.extend(self._check_structural_headings_not_numbered(document))
        issues.extend(self._check_page_volume(document))
        return issues

    def _check_required_sections(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        found_types = set()
        for section in document.sections:
            classified = _classify_section(section.heading)
            if classified:
                found_types.add(classified)

        required = {"abstract", "contents", "introduction", "conclusion", "references"}
        missing = required - found_types
        for section_type in missing:
            issues.append(Issue(
                severity="error",
                category="structure",
                checker=self.name,
                location=IssueLocation(section_name=section_type),
                message=f"Required section '{section_type}' is missing",
                suggestion=f"Add a '{section_type}' section to your document",
                rule_ref="Sec. 6.4",
            ))
        return issues

    def _check_section_order(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        if not document.sections:
            return issues

        classified_order = []
        for section in document.sections:
            classified = _classify_section(section.heading)
            if classified and classified in REQUIRED_ORDER:
                classified_order.append(classified)

        # Check if the order matches expected
        expected_indices = []
        for section_type in classified_order:
            if section_type in REQUIRED_ORDER:
                expected_indices.append(REQUIRED_ORDER.index(section_type))

        for i in range(1, len(expected_indices)):
            if expected_indices[i] < expected_indices[i - 1]:
                issues.append(Issue(
                    severity="error",
                    category="structure",
                    checker=self.name,
                    location=IssueLocation(section_name=classified_order[i]),
                    message=f"Section '{classified_order[i]}' appears out of order",
                    suggestion=f"Move '{classified_order[i]}' to its correct position per GOST Sec. 6.4",
                    rule_ref="Sec. 6.4",
                ))
        return issues

    def _check_structural_headings_not_numbered(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        number_pattern = re.compile(r"^\d+\s+")
        for para in document.paragraphs:
            if para.is_heading and para.heading_level == 1:
                lower_text = para.text.strip().lower()
                # Check if this is a structural heading
                is_structural = any(sh in lower_text for sh in STRUCTURAL_HEADINGS)
                if is_structural and number_pattern.match(para.text.strip()):
                    issues.append(Issue(
                        severity="warning",
                        category="structure",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=para.paragraph_index,
                            context_text=para.text[:80],
                        ),
                        message=f"Structural heading '{para.text}' should NOT be numbered",
                        suggestion="Remove the number prefix from this structural heading",
                        rule_ref="Sec. 6.4",
                    ))
        return issues

    def _check_page_volume(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        threshold = PAGE_THRESHOLDS.get(document.doc_type, 40)
        if document.page_count_body < threshold:
            issues.append(Issue(
                severity="warning",
                category="structure",
                checker=self.name,
                location=IssueLocation(),
                message=f"Page volume ({document.page_count_body} pages) is below minimum ({threshold} pages) for {document.doc_type}",
                suggestion=f"Add more content to reach at least {threshold} pages (excluding appendices, references, abstract)",
                rule_ref="Sec. 6.2",
            ))
        return issues
