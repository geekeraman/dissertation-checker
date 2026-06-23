"""Data structures for parsed DOCX documents."""

from dataclasses import dataclass, field


@dataclass
class ParsedParagraph:
    text: str
    style_name: str
    is_heading: bool
    heading_level: int | None  # 1-9 if heading, None otherwise
    font_name: str | None
    font_size: float | None  # in points
    bold: bool | None
    alignment: str | None  # "left", "center", "right", "justify"
    line_spacing: float | None  # e.g., 1.5
    first_line_indent: float | None  # in cm
    has_page_break_before: bool = False
    paragraph_index: int = 0


@dataclass
class DocumentSection:
    name: str
    heading: str
    start_paragraph_index: int
    end_paragraph_index: int
    level: int  # heading level


@dataclass
class Figure:
    number: str | None  # e.g., "1.1"
    title: str | None
    paragraph_index: int  # where the figure is referenced/located
    caption_paragraph_index: int | None  # paragraph index of caption
    has_caption: bool = False
    caption_position: str | None = None  # "above" or "below"


@dataclass
class Table:
    number: str | None
    title: str | None
    paragraph_index: int
    caption_paragraph_index: int | None
    has_caption: bool = False
    caption_position: str | None = None  # "above" or "below"


@dataclass
class Reference:
    text: str
    paragraph_index: int


@dataclass
class DocumentMetadata:
    title: str | None = None
    author: str | None = None
    language: str | None = None


@dataclass
class DocProperties:
    left_margin_cm: float | None = None
    right_margin_cm: float | None = None
    top_margin_cm: float | None = None
    bottom_margin_cm: float | None = None
    default_font_name: str | None = None
    default_font_size: float | None = None
    default_line_spacing: float | None = None
    page_width_cm: float | None = None
    page_height_cm: float | None = None


@dataclass
class ParsedDocument:
    doc_type: str  # "thesis_humanities" | "thesis_science" | "project"
    paragraphs: list[ParsedParagraph] = field(default_factory=list)
    sections: list[DocumentSection] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    page_count: int = 0
    page_count_body: int = 0
    properties: DocProperties = field(default_factory=DocProperties)
