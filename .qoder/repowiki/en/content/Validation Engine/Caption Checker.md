# Caption Checker

<cite>
**Referenced Files in This Document**
- [captions.py](file://backend/app/checkers/captions.py)
- [base.py](file://backend/app/checkers/base.py)
- [models.py](file://backend/app/core/models.py)
- [structures.py](file://backend/app/parser/structures.py)
- [routes.py](file://backend/app/api/routes.py)
- [runner.py](file://backend/app/runner.py)
- [test_captions.py](file://backend/tests/test_captions.py)
- [design.md](file://docs/design.md)
- [plan.md](file://docs/plan.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document describes the CaptionChecker implementation that validates figure and table captions according to GOST 7.32-2017 standards. It explains how the checker enforces caption numbering, placement, and cross-reference rules, and how it integrates with the parsed document structures. The documentation covers the checking algorithms for caption consistency, sequential numbering, and reference accuracy, and provides examples of common caption issues such as broken references, incorrect numbering, and formatting errors.

## Project Structure
The CaptionChecker resides in the backend application under the checkers module and interacts with the parsed document structures and the reporting framework. The key components are:
- CaptionChecker: Implements caption validation logic
- ParsedDocument and related structures: Provide parsed document data
- Issue and IssueLocation: Define the reporting model
- CheckerRunner: Orchestrates execution of all checkers
- API routes: Integrate the checker into the service pipeline

```mermaid
graph TB
subgraph "Checkers"
CC["CaptionChecker<br/>backend/app/checkers/captions.py"]
BC["BaseChecker<br/>backend/app/checkers/base.py"]
end
subgraph "Parser"
PD["ParsedDocument & Structures<br/>backend/app/parser/structures.py"]
end
subgraph "Core"
IM["Issue & IssueLocation<br/>backend/app/core/models.py"]
end
subgraph "Orchestration"
CR["CheckerRunner<br/>backend/app/runner.py"]
API["API Routes<br/>backend/app/api/routes.py"]
end
API --> CR
CR --> CC
CC --> PD
CC --> IM
CC --> BC
```

**Diagram sources**
- [captions.py:1-108](file://backend/app/checkers/captions.py#L1-L108)
- [base.py:1-17](file://backend/app/checkers/base.py#L1-L17)
- [structures.py:1-89](file://backend/app/parser/structures.py#L1-L89)
- [models.py:1-58](file://backend/app/core/models.py#L1-L58)
- [runner.py:1-25](file://backend/app/runner.py#L1-L25)
- [routes.py:1-75](file://backend/app/api/routes.py#L1-L75)

**Section sources**
- [captions.py:1-108](file://backend/app/checkers/captions.py#L1-L108)
- [structures.py:1-89](file://backend/app/parser/structures.py#L1-L89)
- [models.py:1-58](file://backend/app/core/models.py#L1-L58)
- [runner.py:1-25](file://backend/app/runner.py#L1-L25)
- [routes.py:1-75](file://backend/app/api/routes.py#L1-L75)

## Core Components
- CaptionChecker: Validates figure and table captions per GOST 7.32-2017, focusing on presence, placement, and numbering consistency.
- ParsedDocument and structures: Provide typed data about figures and tables, including numbering, positions, and presence of captions.
- Issue and IssueLocation: Standardized reporting model for captured issues with severity, category, and rule references.
- BaseChecker: Defines the checker interface contract for all validators.
- CheckerRunner: Executes all registered checkers and aggregates results into a Report.

Key validation areas:
- Presence: Missing captions for detected figures/tables
- Placement: Figure captions must be below; table captions must be above
- Numbering: Sequential numbering within chapters for figures

**Section sources**
- [captions.py:8-16](file://backend/app/checkers/captions.py#L8-L16)
- [structures.py:32-49](file://backend/app/parser/structures.py#L32-L49)
- [models.py:18-26](file://backend/app/core/models.py#L18-L26)
- [base.py:9-17](file://backend/app/checkers/base.py#L9-L17)

## Architecture Overview
The CaptionChecker participates in the checker orchestration pipeline. The API receives a DOCX file, parses it into a ParsedDocument, runs all registered checkers via CheckerRunner, and returns a Report containing all issues.

```mermaid
sequenceDiagram
participant Client as "Client"
participant API as "API Routes"
participant Parser as "parse_docx"
participant Runner as "CheckerRunner"
participant Checker as "CaptionChecker"
participant Model as "Issue/Report"
Client->>API : "POST /api/check (file, doc_type)"
API->>Parser : "parse_docx(file_path, doc_type)"
Parser-->>API : "ParsedDocument"
API->>Runner : "run(document, filename)"
Runner->>Checker : "check(document)"
Checker-->>Runner : "list[Issue]"
Runner->>Model : "Report.from_issues()"
Model-->>Runner : "Report"
Runner-->>API : "Report"
API-->>Client : "Report"
```

**Diagram sources**
- [routes.py:36-67](file://backend/app/api/routes.py#L36-L67)
- [runner.py:15-24](file://backend/app/runner.py#L15-L24)
- [captions.py:12-16](file://backend/app/checkers/captions.py#L12-L16)
- [models.py:29-57](file://backend/app/core/models.py#L29-L57)

## Detailed Component Analysis

### CaptionChecker Implementation
The CaptionChecker enforces GOST 7.32-2017 rules for captions:
- Figures: Must have a caption below the figure; numbering must be sequential within chapters
- Tables: Must have a caption above the table

```mermaid
classDiagram
class BaseChecker {
+string name
+string description
+check(document) Issue[]
}
class CaptionChecker {
+string name
+string description
+check(document) Issue[]
-_check_figures(document) Issue[]
-_check_tables(document) Issue[]
}
class Issue {
+string severity
+string category
+string checker
+IssueLocation location
+string message
+string suggestion
+string rule_ref
}
class IssueLocation {
+int paragraph_index
+int page_number
+string section_name
+string context_text
}
class ParsedDocument {
+string doc_type
+ParsedParagraph[] paragraphs
+DocumentSection[] sections
+Figure[] figures
+Table[] tables
+Reference[] references
+DocumentMetadata metadata
+int page_count
+int page_count_body
+DocProperties properties
}
class Figure {
+string number
+string title
+int paragraph_index
+int caption_paragraph_index
+bool has_caption
+string caption_position
}
class Table {
+string number
+string title
+int paragraph_index
+int caption_paragraph_index
+bool has_caption
+string caption_position
}
CaptionChecker --|> BaseChecker
CaptionChecker --> Issue : "produces"
CaptionChecker --> IssueLocation : "uses"
CaptionChecker --> ParsedDocument : "consumes"
ParsedDocument --> Figure : "contains"
ParsedDocument --> Table : "contains"
```

**Diagram sources**
- [captions.py:8-108](file://backend/app/checkers/captions.py#L8-L108)
- [base.py:9-17](file://backend/app/checkers/base.py#L9-L17)
- [models.py:18-26](file://backend/app/core/models.py#L18-L26)
- [structures.py:32-89](file://backend/app/parser/structures.py#L32-L89)

Validation logic highlights:
- Missing captions: Emits an error with suggestions aligned to GOST 7.32-2017
- Incorrect placement: Enforces figure captions below and table captions above
- Sequential numbering: Tracks chapter-based numbering and warns on gaps

**Section sources**
- [captions.py:18-73](file://backend/app/checkers/captions.py#L18-L73)
- [captions.py:75-107](file://backend/app/checkers/captions.py#L75-L107)

### Data Structures for Captions
The parser provides typed structures that the CaptionChecker consumes:
- Figure: includes numbering, title, paragraph indices, caption presence, and caption position
- Table: mirrors Figure with caption presence and position
- ParsedDocument: aggregates figures and tables along with other document metadata

These structures enable precise issue reporting with locations and context.

**Section sources**
- [structures.py:32-49](file://backend/app/parser/structures.py#L32-L49)
- [structures.py:78-89](file://backend/app/parser/structures.py#L78-L89)

### Integration with Checker Orchestration
The CaptionChecker is registered with the CheckerRunner alongside other checkers. The API route handler creates a runner, registers all checkers, and executes them in order.

```mermaid
sequenceDiagram
participant API as "API Routes"
participant Runner as "CheckerRunner"
participant CC as "CaptionChecker"
participant Other as "Other Checkers"
API->>Runner : "create_runner()"
Runner->>CC : "register(CaptionChecker())"
Runner->>Other : "register(...) (other checkers)"
API->>Runner : "run(document, filename)"
Runner->>CC : "check(document)"
CC-->>Runner : "list[Issue]"
Runner->>Other : "check(document)"
Other-->>Runner : "list[Issue]"
Runner-->>API : "Report"
```

**Diagram sources**
- [routes.py:21-28](file://backend/app/api/routes.py#L21-L28)
- [runner.py:8-24](file://backend/app/runner.py#L8-L24)
- [captions.py:12-16](file://backend/app/checkers/captions.py#L12-L16)

**Section sources**
- [routes.py:21-28](file://backend/app/api/routes.py#L21-L28)
- [runner.py:8-24](file://backend/app/runner.py#L8-L24)

### Validation Rules and Cross-References
The CaptionChecker references GOST 7.32-2017 sections for figure and table captions:
- Figure captions: Section 6.5
- Table captions: Section 6.6

These references are included in reported issues to align enforcement with the standard.

**Section sources**
- [captions.py:34](file://backend/app/checkers/captions.py#L34)
- [captions.py:89](file://backend/app/checkers/captions.py#L89)

### Checking Algorithms
- Presence validation: Iterates over figures/tables and reports missing captions
- Placement validation: Checks caption_position and emits errors when misaligned with GOST requirements
- Sequential numbering: Maintains a map of last seen number per chapter and warns on non-sequential entries

```mermaid
flowchart TD
Start(["Start _check_figures"]) --> Iterate["Iterate over document.figures"]
Iterate --> HasCaption{"Has caption?"}
HasCaption --> |No| AddMissing["Add 'missing caption' error"]
HasCaption --> |Yes| CheckBelow{"Caption below?"}
CheckBelow --> |No| AddPlacement["Add 'must be below' error"]
CheckBelow --> |Yes| CheckNumbering{"Has number?"}
CheckNumbering --> |No| NextFig["Next figure"]
CheckNumbering --> |Yes| SplitParts["Split number by '.'"]
SplitParts --> PartsOk{"Two parts?"}
PartsOk --> |No| NextFig
PartsOk --> |Yes| ChapterNum["Get chapter and number"]
ChapterNum --> PrevLast["Get previous number for chapter"]
PrevLast --> SeqCheck{"Is number = last + 1?"}
SeqCheck --> |No| AddWarning["Add 'not sequential' warning"]
SeqCheck --> |Yes| UpdatePrev["Update last number for chapter"]
AddWarning --> NextFig
UpdatePrev --> NextFig
NextFig --> Iterate
Iterate --> End(["End _check_figures"])
```

**Diagram sources**
- [captions.py:18-73](file://backend/app/checkers/captions.py#L18-L73)

**Section sources**
- [captions.py:18-73](file://backend/app/checkers/captions.py#L18-L73)

### Common Caption Issues and Examples
Common issues validated by the CaptionChecker include:
- Missing captions for figures/tables
- Incorrect caption placement (figure caption above or table caption below)
- Non-sequential numbering within chapters for figures

The test suite demonstrates these scenarios and ensures the checker produces the expected issues.

**Section sources**
- [test_captions.py:13-26](file://backend/tests/test_captions.py#L13-L26)
- [test_captions.py:27-36](file://backend/tests/test_captions.py#L27-L36)
- [test_captions.py:37-46](file://backend/tests/test_captions.py#L37-L46)
- [test_captions.py:47-55](file://backend/tests/test_captions.py#L47-L55)
- [test_captions.py:57-66](file://backend/tests/test_captions.py#L57-L66)

## Dependency Analysis
The CaptionChecker depends on:
- BaseChecker for the checker interface
- Issue and IssueLocation for reporting
- ParsedDocument structures for input data
- No external libraries are imported, keeping dependencies minimal

```mermaid
graph LR
BC["BaseChecker"] --> CC["CaptionChecker"]
IM["Issue/IssueLocation"] --> CC
PS["ParsedDocument/Figure/Table"] --> CC
```

**Diagram sources**
- [captions.py:3-5](file://backend/app/checkers/captions.py#L3-L5)
- [base.py:9-17](file://backend/app/checkers/base.py#L9-L17)
- [models.py:18-26](file://backend/app/core/models.py#L18-L26)
- [structures.py:32-89](file://backend/app/parser/structures.py#L32-L89)

**Section sources**
- [captions.py:3-5](file://backend/app/checkers/captions.py#L3-L5)
- [base.py:9-17](file://backend/app/checkers/base.py#L9-L17)
- [models.py:18-26](file://backend/app/core/models.py#L18-L26)
- [structures.py:32-89](file://backend/app/parser/structures.py#L32-L89)

## Performance Considerations
- Complexity: O(n) over the number of figures and tables, with constant-time operations per item
- Memory: Minimal, storing only a small dictionary for chapter-based numbering
- Scalability: The checker scales linearly with document size; no heavy computations are performed

## Troubleshooting Guide
- Missing captions: Ensure figures/tables have captions and that has_caption is set appropriately in the parsed structures
- Incorrect placement: Verify caption_position is set correctly ("below" for figures, "above" for tables)
- Non-sequential numbering: Ensure chapter-based numbering increments by 1 within each chapter

Integration tips:
- Confirm that the CaptionChecker is registered with the CheckerRunner
- Validate that the API route invokes the runner and returns a Report

**Section sources**
- [routes.py:21-28](file://backend/app/api/routes.py#L21-L28)
- [runner.py:8-24](file://backend/app/runner.py#L8-L24)
- [test_captions.py:13-26](file://backend/tests/test_captions.py#L13-L26)

## Conclusion
The CaptionChecker provides targeted validation of figure and table captions according to GOST 7.32-2017, focusing on presence, placement, and sequential numbering. It integrates seamlessly into the checker orchestration pipeline and produces standardized issues with rule references. The implementation is straightforward, efficient, and easily extensible for future enhancements.