"""CaptionChecker — validates figure and table captions per GOST 7.32-2017 Sec. 6.5/6.6."""

from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument

FIGURE_PREFIXES = ("сурет", "рисунок", "figure", "fig.")
TABLE_PREFIXES = ("кесте", "таблица", "table")


class CaptionChecker(BaseChecker):
    name = "captions"
    description = "Validates figure and table captions per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_figures(document))
        issues.extend(self._check_tables(document))
        return issues

    def _check_figures(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        prev_number_parts: dict[str, int] = {}  # chapter -> last number

        for fig in document.figures:
            if not fig.has_caption:
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=fig.paragraph_index,
                        context_text="Figure without caption",
                    ),
                    message="Figure is missing a caption",
                    suggestion="Add a caption below the figure in format 'Сурет X.Y — Title'",
                    rule_ref="Sec. 6.5",
                ))
                continue

            if fig.caption_position != "below":
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=fig.caption_paragraph_index,
                        context_text=fig.title or "",
                    ),
                    message="Figure caption must be placed BELOW the figure",
                    suggestion="Move the figure caption to below the figure",
                    rule_ref="Sec. 6.5",
                ))

            # Check caption format (Kazakh: "Сурет X.Y", Russian: "Рисунок X.Y")
            if fig.has_caption and fig.title:
                title_lower = fig.title.strip().lower()
                has_valid_prefix = any(title_lower.startswith(prefix) for prefix in FIGURE_PREFIXES)
                if not has_valid_prefix:
                    issues.append(Issue(
                        severity="warning",
                        category="captions",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=fig.caption_paragraph_index,
                            context_text=fig.title[:80] if fig.title else "",
                        ),
                        message="Figure caption should start with 'Сурет' (Kazakh), 'Рисунок' (Russian), or 'Figure'",
                        suggestion="Format caption as 'Сурет X.Y – Title' per GOST standard",
                        rule_ref="Sec. 6.5",
                    ))

            # Check sequential numbering
            if fig.number:
                parts = fig.number.split(".")
                if len(parts) == 2:
                    chapter, num = parts[0], int(parts[1]) if parts[1].isdigit() else 0
                    last = prev_number_parts.get(chapter, 0)
                    if num != last + 1 and last > 0:
                        issues.append(Issue(
                            severity="warning",
                            category="captions",
                            checker=self.name,
                            location=IssueLocation(
                                paragraph_index=fig.paragraph_index,
                                context_text=fig.title or "",
                            ),
                            message=f"Figure numbering not sequential: expected {chapter}.{last + 1}, got {fig.number}",
                            suggestion="Ensure figures are numbered sequentially within each chapter",
                            rule_ref="Sec. 6.5",
                        ))
                    prev_number_parts[chapter] = num

        return issues

    def _check_tables(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        for table in document.tables:
            if not table.has_caption:
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=table.paragraph_index,
                        context_text="Table without caption",
                    ),
                    message="Table is missing a caption",
                    suggestion="Add a caption above the table in format 'Кесте X.Y — Title'",
                    rule_ref="Sec. 6.6",
                ))
                continue

            if table.caption_position != "above":
                issues.append(Issue(
                    severity="error",
                    category="captions",
                    checker=self.name,
                    location=IssueLocation(
                        paragraph_index=table.caption_paragraph_index,
                        context_text=table.title or "",
                    ),
                    message="Table caption must be placed ABOVE the table",
                    suggestion="Move the table caption to above the table",
                    rule_ref="Sec. 6.6",
                ))

            # Check caption format (Kazakh: "Кесте X.Y", Russian: "Таблица X.Y")
            if table.has_caption and table.title:
                title_lower = table.title.strip().lower()
                has_valid_prefix = any(title_lower.startswith(prefix) for prefix in TABLE_PREFIXES)
                if not has_valid_prefix:
                    issues.append(Issue(
                        severity="warning",
                        category="captions",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=table.caption_paragraph_index,
                            context_text=table.title[:80] if table.title else "",
                        ),
                        message="Table caption should start with 'Кесте' (Kazakh), 'Таблица' (Russian), or 'Table'",
                        suggestion="Format caption as 'Кесте X.Y – Title' per GOST standard",
                        rule_ref="Sec. 6.6",
                    ))

        return issues
