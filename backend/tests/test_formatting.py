"""Tests for FormattingChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.formatting import FormattingChecker
from app.parser.structures import DocProperties


class TestFormattingChecker:
    def setup_method(self):
        self.checker = FormattingChecker()

    def test_no_issues_for_correct_formatting(self):
        paragraphs = [
            make_paragraph("Body text", font_name="Times New Roman", font_size=14.0,
                           alignment="justify", line_spacing=1.5, paragraph_index=0),
        ]
        props = DocProperties(
            left_margin_cm=3.0, right_margin_cm=1.0,
            top_margin_cm=2.0, bottom_margin_cm=2.0,
        )
        doc = make_document(paragraphs=paragraphs, properties=props)
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_wrong_font(self):
        paragraphs = [
            make_paragraph("Text", font_name="Arial", font_size=14.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        font_issues = [i for i in issues if "font" in i.message.lower()]
        assert len(font_issues) > 0

    def test_wrong_font_size(self):
        paragraphs = [
            make_paragraph("Text", font_size=12.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        size_issues = [i for i in issues if "size" in i.message.lower() or "14" in i.message]
        assert len(size_issues) > 0

    def test_wrong_margins(self):
        props = DocProperties(
            left_margin_cm=2.0, right_margin_cm=2.0,
            top_margin_cm=2.0, bottom_margin_cm=2.0,
        )
        doc = make_document(properties=props)
        issues = self.checker.check(doc)
        margin_issues = [i for i in issues if "margin" in i.message.lower()]
        assert len(margin_issues) > 0

    def test_wrong_line_spacing(self):
        paragraphs = [
            make_paragraph("Text", line_spacing=1.0, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        spacing_issues = [i for i in issues if "spacing" in i.message.lower()]
        assert len(spacing_issues) > 0

    def test_heading_not_uppercase(self):
        paragraphs = [
            make_paragraph("кіріспе", is_heading=True, heading_level=1, bold=True,
                           paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        case_issues = [i for i in issues if "uppercase" in i.message.lower() or "capital" in i.message.lower()]
        assert len(case_issues) > 0

    def test_heading_ends_with_period(self):
        paragraphs = [
            make_paragraph("КІРІСПЕ.", is_heading=True, heading_level=1, bold=True,
                           paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        period_issues = [i for i in issues if "period" in i.message.lower()]
        assert len(period_issues) > 0

    def test_text_not_justified(self):
        paragraphs = [
            make_paragraph("Body text", alignment="left", paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        align_issues = [i for i in issues if "justif" in i.message.lower() or "alignment" in i.message.lower()]
        assert len(align_issues) > 0
