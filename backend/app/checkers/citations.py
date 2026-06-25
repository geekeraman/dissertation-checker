"""CitationChecker — validates citation and reference formatting per GOST 7.32-2017 Sec. 6.8."""

import re
from app.checkers.base import BaseChecker
from app.core.models import Issue, IssueLocation
from app.parser.structures import ParsedDocument


# Pattern to match bracket-style citations like [1], [2,3], [1-5]
BRACKET_CITATION = re.compile(r"\[(\d+(?:[,\s\-–]\d+)*)\]")
# Pattern to match author-year citations like (Author, 2024)
AUTHOR_YEAR_CITATION = re.compile(r"\(([A-ZА-Я][a-zа-я]+(?:\s(?:et al|и др)),?\s\d{4})\)")


class CitationChecker(BaseChecker):
    name = "citations"
    description = "Validates citation and reference formatting per GOST 7.32-2017"

    def check(self, document: ParsedDocument) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._check_citation_reference_match(document))
        issues.extend(self._check_reference_order(document))
        return issues

    def _extract_citations(self, document: ParsedDocument) -> dict[int, list[int]]:
        """Extract all bracket-style citations from body text. Returns {paragraph_index: [citation_numbers]}."""
        citations: dict[int, list[int]] = {}
        for para in document.paragraphs:
            if para.is_heading:
                continue
            matches = BRACKET_CITATION.findall(para.text)
            if matches:
                nums = []
                for match in matches:
                    for part in re.split(r"[,\s]", match):
                        part = part.strip().replace("–", "-")
                        if "-" in part:
                            start, end = part.split("-", 1)
                            if start.isdigit() and end.isdigit():
                                nums.extend(range(int(start), int(end) + 1))
                        elif part.isdigit():
                            nums.append(int(part))
                if nums:
                    citations[para.paragraph_index] = nums
        return citations

    def _extract_reference_numbers(self, document: ParsedDocument) -> dict[int, str]:
        """Extract reference numbers from the reference list. Returns {number: reference_text}."""
        refs: dict[int, str] = {}
        ref_num = re.compile(r"^\[(\d+)\]")
        for ref in document.references:
            match = ref_num.match(ref.text.strip())
            if match:
                refs[int(match.group(1))] = ref.text
        return refs

    def _check_citation_reference_match(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        citations = self._extract_citations(document)
        references = self._extract_reference_numbers(document)

        cited_numbers = set()
        for para_idx, nums in citations.items():
            for num in nums:
                cited_numbers.add(num)
                if references and num not in references:
                    para = next(
                        (p for p in document.paragraphs if p.paragraph_index == para_idx), None
                    )
                    issues.append(Issue(
                        severity="error",
                        category="citations",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=para_idx,
                            context_text=para.text[:80] if para else "",
                        ),
                        message=f"Citation [{num}] has no matching reference entry",
                        suggestion=f"Add reference [{num}] to the reference list or remove the citation",
                        rule_ref="Sec. 6.8",
                    ))

        # Check for uncited references
        for ref_num, ref_text in references.items():
            if ref_num not in cited_numbers:
                issues.append(Issue(
                    severity="warning",
                    category="citations",
                    checker=self.name,
                    location=IssueLocation(context_text=ref_text[:80]),
                    message=f"Reference [{ref_num}] is not cited in the text",
                    suggestion="Either cite this reference in the text or remove it from the reference list",
                    rule_ref="Sec. 6.8",
                ))

        return issues

    def _check_reference_order(self, document: ParsedDocument) -> list[Issue]:
        issues = []
        if len(document.references) < 2:
            return issues

        # Check if references use numbered format — if so, alphabetical order doesn't apply
        ref_num = re.compile(r"^\[\d+\]")
        is_numbered = all(ref_num.match(r.text.strip()) for r in document.references[:3] if r.text.strip())

        if not is_numbered:
            # Check alphabetical order for non-numbered references
            for i in range(1, len(document.references)):
                prev = document.references[i - 1].text.strip().lower()
                curr = document.references[i].text.strip().lower()
                if prev and curr and prev > curr:
                    issues.append(Issue(
                        severity="warning",
                        category="citations",
                        checker=self.name,
                        location=IssueLocation(
                            paragraph_index=document.references[i].paragraph_index,
                            context_text=document.references[i].text[:80],
                        ),
                        message="References are not in alphabetical order",
                        suggestion="Sort the reference list alphabetically by author name",
                        rule_ref="Sec. 6.8",
                    ))
                    break  # Report once, not for every pair

        return issues
