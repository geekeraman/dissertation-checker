"""Tests for StructureChecker."""

import pytest
from tests.conftest import make_paragraph, make_document
from app.checkers.structure import StructureChecker
from app.parser.structures import DocumentSection


class TestStructureChecker:
    def setup_method(self):
        self.checker = StructureChecker()

    def test_no_issues_for_correct_structure(self):
        sections = [
            DocumentSection("Title", "TITLE PAGE", 0, 2, 1),
            DocumentSection("Abstract", "РЕФЕРАТ", 3, 8, 1),
            DocumentSection("Contents", "МАЗМҰНЫ", 9, 15, 1),
            DocumentSection("Introduction", "КІРІСПЕ", 16, 30, 1),
            DocumentSection("Main", "1 НЕГІЗГІ БӨЛІМ", 31, 80, 1),
            DocumentSection("Conclusion", "ҚОРЫТЫНДЫ", 81, 90, 1),
            DocumentSection("References", "ПАЙДАЛАНЫЛҒАН ӘДЕБИЕТТЕР ТІЗІМІ", 91, 100, 1),
        ]
        doc = make_document(sections=sections, page_count_body=50, doc_type="thesis_science")
        issues = self.checker.check(doc)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_missing_required_heading(self):
        sections = [
            DocumentSection("Title", "TITLE PAGE", 0, 2, 1),
            DocumentSection("Introduction", "КІРІСПЕ", 3, 30, 1),
        ]
        doc = make_document(sections=sections)
        issues = self.checker.check(doc)
        missing = [i for i in issues if "missing" in i.message.lower() or "required" in i.message.lower()]
        assert len(missing) > 0

    def test_wrong_section_order(self):
        sections = [
            DocumentSection("Conclusion", "ҚОРЫТЫНДЫ", 0, 10, 1),
            DocumentSection("Introduction", "КІРІСПЕ", 11, 30, 1),
        ]
        doc = make_document(sections=sections)
        issues = self.checker.check(doc)
        order_issues = [i for i in issues if "order" in i.message.lower()]
        assert len(order_issues) > 0

    def test_structural_heading_numbered(self):
        paragraphs = [
            make_paragraph("1 МАЗМҰНЫ", is_heading=True, heading_level=1, paragraph_index=0),
        ]
        doc = make_document(paragraphs=paragraphs)
        issues = self.checker.check(doc)
        numbered = [i for i in issues if "not numbered" in i.message.lower() or "number" in i.message.lower()]
        assert len(numbered) > 0

    def test_page_volume_below_minimum(self):
        doc = make_document(page_count_body=20, doc_type="thesis_science")
        issues = self.checker.check(doc)
        volume = [i for i in issues if "volume" in i.message.lower() or "page" in i.message.lower()]
        assert len(volume) > 0

    def test_page_volume_project_minimum(self):
        doc = make_document(page_count_body=30, doc_type="project")
        issues = self.checker.check(doc)
        volume = [i for i in issues if "volume" in i.message.lower() or "page" in i.message.lower()]
        assert len(volume) > 0

    def test_page_volume_humanities_minimum(self):
        doc = make_document(page_count_body=35, doc_type="thesis_humanities")
        issues = self.checker.check(doc)
        volume = [i for i in issues if "volume" in i.message.lower() or "page" in i.message.lower()]
        assert len(volume) > 0

    def test_section_missing_page_break(self):
        """Section should start on new page."""
        paragraphs = [
            make_paragraph("Previous text", paragraph_index=0),
            make_paragraph("КІРІСПЕ", is_heading=True, heading_level=1,
                          has_page_break_before=False, paragraph_index=1),
        ]
        sections = [
            DocumentSection(name="section", heading="КІРІСПЕ",
                          start_paragraph_index=1, end_paragraph_index=5, level=1),
        ]
        doc = make_document(paragraphs=paragraphs, sections=sections)
        issues = self.checker.check(doc)
        page_break = [i for i in issues if "new page" in i.message.lower()]
        assert len(page_break) > 0

    def test_abstract_too_short(self):
        """Abstract with too few words should get info."""
        paragraphs = [
            make_paragraph("АҢДАТПА", is_heading=True, heading_level=1, paragraph_index=0),
            make_paragraph("Short abstract.", paragraph_index=1),
        ]
        sections = [
            DocumentSection(name="section", heading="АҢДАТПА",
                          start_paragraph_index=0, end_paragraph_index=1, level=1),
        ]
        doc = make_document(paragraphs=paragraphs, sections=sections)
        issues = self.checker.check(doc)
        word_count = [i for i in issues if "short" in i.message.lower() or "word" in i.message.lower()]
        assert len(word_count) > 0
