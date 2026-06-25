import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface IssueLocation {
  paragraph_index: number | null;
  page_number: number | null;
  section_name: string | null;
  context_text: string;
}

export interface Issue {
  severity: 'error' | 'warning' | 'info';
  category: string;
  checker: string;
  location: IssueLocation;
  message: string;
  suggestion: string;
  rule_ref: string;
}

export interface Report {
  id: string;
  filename: string;
  checked_at: string;
  doc_type: string;
  total_issues: number;
  issues_by_severity: Record<string, number>;
  issues_by_category: Record<string, number>;
  issues: Issue[];
}

export async function checkDissertation(
  file: File,
  docType: string
): Promise<Report> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('doc_type', docType);
  const response = await axios.post<Report>(`${API_BASE}/check`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getReport(id: string): Promise<Report> {
  const response = await axios.get<Report>(`${API_BASE}/reports/${id}`);
  return response.data;
}
