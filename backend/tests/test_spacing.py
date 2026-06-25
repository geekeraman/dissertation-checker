"""Tests for SpacingChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.spacing import SpacingChecker


class TestSpacingChecker:
    def setup_method(self):
        self.checker = SpacingChecker()

    def test_no_issues_for_clean_text(self):
        paragraphs = [
            make_paragraph("Normal paragraph text.", paragraph_index=0),
            make_paragraph("Another paragraph.", paragraph_index=1),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        assert len(issues) == 0

    def test_trailing_whitespace(self):
        paragraphs = [
            make_paragraph("Text with trailing spaces   ", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        trailing = [i for i in issues if "trailing" in i.message.lower()]
        assert len(trailing) > 0

    def test_multiple_consecutive_spaces(self):
        paragraphs = [
            make_paragraph("Text  with  double  spaces", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        spaces = [i for i in issues if "consecutive" in i.message.lower() or "multiple" in i.message.lower()]
        assert len(spaces) > 0

    def test_empty_paragraphs_between_sections(self):
        paragraphs = [
            make_paragraph("Section text", paragraph_index=0),
            make_paragraph("", paragraph_index=1),
            make_paragraph("", paragraph_index=2),
            make_paragraph("", paragraph_index=3),
            make_paragraph("Next section", paragraph_index=4),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        blank = [i for i in issues if "blank" in i.message.lower() or "empty" in i.message.lower()]
        assert len(blank) > 0

    def test_tab_characters(self):
        paragraphs = [
            make_paragraph("\tTabbed text", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        tabs = [i for i in issues if "tab" in i.message.lower()]
        assert len(tabs) > 0
