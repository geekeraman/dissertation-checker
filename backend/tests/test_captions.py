"""Tests for CaptionChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.captions import CaptionChecker
from app.parser.structures import Figure, Table


class TestCaptionChecker:
    def setup_method(self):
        self.checker = CaptionChecker()

    def test_no_issues_for_correct_captions(self):
        figures = [
            Figure(number="1.1", title="Сурет 1.1 - Diagram", paragraph_index=10,
                   has_caption=True, caption_paragraph_index=11, caption_position="below"),
        ]
        tables = [
            Table(number="1.1", title="Кесте 1.1 - Data", paragraph_index=20,
                  has_caption=True, caption_paragraph_index=19, caption_position="above"),
        ]
        doc = make_document(figures=figures, tables=tables)
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_figure_missing_caption(self):
        figures = [
            Figure(number=None, title=None, paragraph_index=10,
                   has_caption=False, caption_paragraph_index=None),
        ]
        doc = make_document(figures=figures)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "missing" in i.message.lower() or "caption" in i.message.lower()]
        assert len(missing) > 0

    def test_figure_caption_above_instead_of_below(self):
        figures = [
            Figure(number="1.1", title="Сурет 1.1", paragraph_index=10,
                   has_caption=True, caption_paragraph_index=9, caption_position="above"),
        ]
        doc = make_document(figures=figures)
        issues = self.checker.check(doc)
        position = [i for i in issues if "below" in i.message.lower() or "position" in i.message.lower()]
        assert len(position) > 0

    def test_table_caption_below_instead_of_above(self):
        tables = [
            Table(number="1.1", title="Кесте 1.1", paragraph_index=20,
                  has_caption=True, caption_paragraph_index=21, caption_position="below"),
        ]
        doc = make_document(tables=tables)
        issues = self.checker.check(doc)
        position = [i for i in issues if "above" in i.message.lower() or "position" in i.message.lower()]
        assert len(position) > 0

    def test_table_missing_caption(self):
        tables = [
            Table(number=None, title=None, paragraph_index=20,
                  has_caption=False, caption_paragraph_index=None),
        ]
        doc = make_document(tables=tables)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "missing" in i.message.lower() or "caption" in i.message.lower()]
        assert len(missing) > 0
