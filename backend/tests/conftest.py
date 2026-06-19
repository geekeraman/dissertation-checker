"""Shared test fixtures."""

import pytest
from app.parser.structures import (
    ParsedDocument, ParsedParagraph, DocumentSection,
    Figure, Table, Reference, DocumentMetadata, DocProperties,
)


def make_paragraph(
    text: str = "Sample text",
    style_name: str = "Normal",
    is_heading: bool = False,
    heading_level: int | None = None,
    font_name: str | None = "Times New Roman",
    font_size: float | None = 14.0,
    bold: bool | None = False,
    alignment: str | None = "justify",
    line_spacing: float | None = 1.5,
    first_line_indent: float | None = 1.0,
    has_page_break_before: bool = False,
    paragraph_index: int = 0,
) -> ParsedParagraph:
    return ParsedParagraph(
        text=text, style_name=style_name, is_heading=is_heading,
        heading_level=heading_level, font_name=font_name, font_size=font_size,
        bold=bold, alignment=alignment, line_spacing=line_spacing,
        first_line_indent=first_line_indent,
        has_page_break_before=has_page_break_before,
        paragraph_index=paragraph_index,
    )


def make_document(
    doc_type: str = "thesis_science",
    paragraphs: list[ParsedParagraph] | None = None,
    sections: list[DocumentSection] | None = None,
    figures: list[Figure] | None = None,
    tables: list[Table] | None = None,
    references: list[Reference] | None = None,
    page_count: int = 50,
    page_count_body: int = 45,
    properties: DocProperties | None = None,
) -> ParsedDocument:
    return ParsedDocument(
        doc_type=doc_type,
        paragraphs=paragraphs or [],
        sections=sections or [],
        figures=figures or [],
        tables=tables or [],
        references=references or [],
        metadata=DocumentMetadata(),
        page_count=page_count,
        page_count_body=page_count_body,
        properties=properties or DocProperties(),
    )
