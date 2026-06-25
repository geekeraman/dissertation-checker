"""FormattingChecker — validates page layout and typography per GOST 7.32-2017 Sec. 6.2."""

from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


EXPECTED_FONT = "Times New Roman"
EXPECTED_FONT_SIZE = 14.0
EXPECTED_LINE_SPACING = 1.5
EXPECTED_MARGINS = {"left": 3.0, "right": 1.0, "top": 2.0, "bottom": 2.0}
MARGIN_TOLERANCE = 0.2  # cm
EXPECTED_INDENT = 1.25  # cm
INDENT_TOLERANCE = 0.15  # cm


class FormattingChecker(BaseChecker):
    name = "formatting"
    description = "Validates page layout, typography, and heading styles per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_margins(document))
        issues.extend(self._check_paragraph_formatting(document))
        issues.extend(self._check_heading_style(document))
        issues.extend(self._check_paragraph_indent(document))
        issues.extend(self._check_page_numbering(document))
        return issues

    def _check_margins(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        props = document.properties
        margin_checks = {
            "left": (props.left_margin_cm, EXPECTED_MARGINS["left"]),
            "right": (props.right_margin_cm, EXPECTED_MARGINS["right"]),
            "top": (props.top_margin_cm, EXPECTED_MARGINS["top"]),
            "bottom": (props.bottom_margin_cm, EXPECTED_MARGINS["bottom"]),
        }
        for side, (actual, expected) in margin_checks.items():
            if actual is not None and abs(actual - expected) > MARGIN_TOLERANCE:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(),
                    message=f"{side.capitalize()} margin is {actual:.1f}cm, expected {expected:.1f}cm",
                    suggestion=f"Set {side} margin to {expected:.0f}cm in Page Layout settings",
                    rule_ref="Sec. 6.2",
                ))
        return issues

    def _check_paragraph_formatting(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.text.strip():
                continue

            # Skip headings for font/alignment checks (checked separately)
            if para.is_heading:
                continue

            # Font name
            if para.font_name and para.font_name != EXPECTED_FONT:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Font is '{para.font_name}', expected '{EXPECTED_FONT}'",
                    suggestion=f"Change font to {EXPECTED_FONT}",
                    rule_ref="Sec. 6.2",
                ))

            # Font size
            if para.font_size and abs(para.font_size - EXPECTED_FONT_SIZE) > 0.5:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Font size is {para.font_size}pt, expected {EXPECTED_FONT_SIZE}pt",
                    suggestion=f"Change font size to {EXPECTED_FONT_SIZE}pt",
                    rule_ref="Sec. 6.2",
                ))

            # Line spacing
            if para.line_spacing and abs(para.line_spacing - EXPECTED_LINE_SPACING) > 0.1:
                issues.append(Issue(
                    severity="error",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Line spacing is {para.line_spacing}, expected {EXPECTED_LINE_SPACING}",
                    suggestion="Set line spacing to 1.5",
                    rule_ref="Sec. 6.2",
                ))

            # Alignment
            if para.alignment and para.alignment != "justify":
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=para.text[:80],
                    ),
                    message=f"Text alignment is '{para.alignment}', expected 'justify'",
                    suggestion="Set paragraph alignment to Justify",
                    rule_ref="Sec. 6.2",
                ))

        return issues

    def _check_heading_style(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.is_heading or not para.text.strip():
                continue

            text = para.text.strip()

            # Uppercase check
            if text != text.upper():
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message=f"Heading should be uppercase: '{text}'",
                    suggestion="Convert heading text to UPPERCASE",
                    rule_ref="Sec. 6.2",
                ))

            # No period at end
            if text.endswith("."):
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message="Heading should not end with a period",
                    suggestion="Remove the trailing period from the heading",
                    rule_ref="Sec. 6.2",
                ))

            # Bold check
            if para.bold is False:
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message="Heading should be bold",
                    suggestion="Apply bold formatting to the heading",
                    rule_ref="Sec. 6.2",
                ))

            # Center alignment check
            if para.alignment and para.alignment != "center":
                issues.append(Issue(
                    severity="warning",
                    category="formatting",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=para.paragraph_index,
                        context_text=text[:80],
                    ),
                    message=f"Heading should be centered, but is '{para.alignment}'",
                    suggestion="Set heading alignment to Center",
                    rule_ref="Sec. 6.2",
                ))

        return issues

    def _check_paragraph_indent(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for para in document.paragraphs:
            if not para.text.strip() or para.is_heading:
                continue
            if para.first_line_indent is not None:
                if abs(para.first_line_indent - EXPECTED_INDENT) > INDENT_TOLERANCE:
                    issues.append(Issue(
                        severity="warning",
                        category="formatting",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=para.paragraph_index,
                            context_text=para.text[:80],
                        ),
                        message=f"First-line indent is {para.first_line_indent:.2f}cm, expected {EXPECTED_INDENT}cm",
                        suggestion=f"Set paragraph first-line indent to {EXPECTED_INDENT}cm",
                        rule_ref="Sec. 6.2",
                    ))
        return issues

    def _check_page_numbering(self, document: ParsedDocument) -> list[Issue]:
        """Advisory check — python-docx has limited page number detection."""
        issues = []
        # Only provide advisory if page count is 0 (suggests no page numbers detected)
        if document.page_count == 0:
            issues.append(Issue(
                severity="info",
                category="formatting",
                checker=self.name,
                location=IssueLocation(),
                message="Page numbering could not be verified — ensure Arabic numerals at bottom-center",
                suggestion="Add page numbers: Insert > Page Number > Bottom of Page > Center",
                rule_ref="Sec. 6.2",
            ))
        return issues
