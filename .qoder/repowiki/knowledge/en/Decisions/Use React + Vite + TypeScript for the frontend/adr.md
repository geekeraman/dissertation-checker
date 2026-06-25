# Use React + Vite + TypeScript for the frontend

_Source: coding plans from commit period 6fcc7b3 → 7c95201 — records intent at planning time; the implementation may lag or differ._

**Status:** accepted

## Context
The project needs a modern, responsive user interface for uploading `.docx` files and displaying detailed validation reports with filtering capabilities. The team requires a development environment with fast hot-reloading and strong type safety to match the backend's strict data contracts.

## Decision drivers
- Developer experience (fast dev server)
- Type safety across the UI layer
- Component reusability for report elements

## Considered options
- **React + Vite + TypeScript** — pros: Vite provides significantly faster build times and HMR compared to Webpack; TypeScript ensures consistency with backend API types; large ecosystem for UI components.; cons: Requires setting up a separate Node.js environment and build pipeline distinct from the Python backend.
- **Server-side rendered templates (e.g., Jinja2)** _(rejected)_ — pros: Single deployment artifact; no separate frontend build step.; cons: Poor interactivity for dynamic filtering and real-time upload feedback; harder to maintain complex UI state.

## Decision
Scaffold the frontend using `npm create vite@latest` with React and TypeScript. The architecture separates concerns into `api/client.ts` for Axios-based communication, reusable components (`IssueCard`, `ReportSummary`), and page-level containers (`UploadPage`, `ReportPage`).

## Consequences
The project now maintains two separate runtimes (Python/FastAPI and Node/Vite). The frontend must handle CORS and asynchronous state management for file uploads and report rendering.