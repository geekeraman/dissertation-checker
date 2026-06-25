"""Tests for CitationChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.citations import CitationChecker
from app.parser.structures import Reference


class TestCitationChecker:
    def setup_method(self):
        self.checker = CitationChecker()

    def test_no_issues_for_matching_citations(self):
        paragraphs = [
            make_paragraph("As shown in [1], the method works.", paragraph_index=0),
            make_paragraph("КІРІСПЕ", is_heading=True, heading_level=1, paragraph_index=1),
        ]
        references = [
            Reference(text="[1] Author, Title, Journal, 2024", paragraph_index=50),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_citation_without_reference(self):
        paragraphs = [
            make_paragraph("As shown in [5], the result is clear.", paragraph_index=0),
        ]
        references = [
            Reference(text="[1] Some other reference", paragraph_index=50),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "no matching" in i.message.lower() or "missing" in i.message.lower()]
        assert len(missing) > 0

    def test_reference_not_cited(self):
        paragraphs = [
            make_paragraph("No citations in this text.", paragraph_index=0),
        ]
        references = [
            Reference(text="[1] Author, Title, 2024", paragraph_index=50),
            Reference(text="[2] Another author, 2023", paragraph_index=51),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        uncited = [i for i in issues if "not cited" in i.message.lower() or "unused" in i.message.lower()]
        assert len(uncited) > 0

    def test_references_not_alphabetical(self):
        references = [
            Reference(text="Zhang, A. (2024). Title", paragraph_index=50),
            Reference(text="Adams, B. (2023). Title", paragraph_index=51),
        ]
        paragraphs = [
            make_paragraph("КІРІСПЕ", is_heading=True, heading_level=1, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        order = [i for i in issues if "alphabetical" in i.message.lower() or "order" in i.message.lower()]
        assert len(order) > 0

    def test_mixed_citation_styles(self):
        paragraphs = [
            make_paragraph("As shown in [1], and (Smith, 2024) confirmed.", paragraph_index=0),
        ]
        references = [
            Reference(text="[1] Author, Title, 2024", paragraph_index=50),
        ]
        doc = make_document(paragraphs=paragraphs, references=references)
        issues = self.checker.check(doc)
        consistency = [i for i in issues if "inconsistent" in i.message.lower() or "mix" in i.message.lower()]
        assert len(consistency) > 0
