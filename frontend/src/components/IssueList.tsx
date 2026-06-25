import { useMemo, useState } from 'react';
import type { Issue } from '../api/client';
import { IssueCard } from './IssueCard';

interface IssueListProps {
  issues: Issue[];
}

type Severity = 'all' | 'error' | 'warning' | 'info';

export function IssueList({ issues }: IssueListProps) {
  const [severityFilter, setSeverityFilter] = useState<Severity>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const categories = useMemo(
    () => Array.from(new Set(issues.map((i) => i.category))).sort(),
    [issues]
  );

  const filtered = useMemo(
    () =>
      issues.filter((i) => {
        if (severityFilter !== 'all' && i.severity !== severityFilter) return false;
        if (categoryFilter !== 'all' && i.category !== categoryFilter) return false;
        return true;
      }),
    [issues, severityFilter, categoryFilter]
  );

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3 border-b border-[#e8eaed] pb-4">
        <span className="text-sm text-[#5f6368]">Filter by:</span>

        <Select
          value={severityFilter}
          onChange={(v) => setSeverityFilter(v as Severity)}
          options={[
            { value: 'all', label: 'All severities' },
            { value: 'error', label: 'Errors' },
            { value: 'warning', label: 'Warnings' },
            { value: 'info', label: 'Info' },
          ]}
        />

        <Select
          value={categoryFilter}
          onChange={setCategoryFilter}
          options={[
            { value: 'all', label: 'All categories' },
            ...categories.map((c) => ({ value: c, label: c })),
          ]}
        />

        <span className="ml-auto text-sm text-[#5f6368]">
          Showing {filtered.length} of {issues.length} issues
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-lg border border-[#dadce0] bg-white px-6 py-10 text-center">
          <p className="text-sm font-medium text-[#202124]">
            No issues match your filters
          </p>
          <p className="mt-1 text-sm text-[#5f6368]">
            Try clearing the filters to see all {issues.length} findings.
          </p>
        </div>
      ) : (
        <div>
          {filtered.map((issue, idx) => (
            <IssueCard key={idx} issue={issue} />
          ))}
        </div>
      )}
    </div>
  );
}

interface Option {
  value: string;
  label: string;
}

function Select({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: Option[];
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none rounded border border-[#dadce0] bg-white py-1.5 pl-3 pr-8 text-sm text-[#202124] hover:border-[#bdc1c6] focus:border-[#1a73e8] focus:outline-none"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#5f6368]"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </div>
  );
}
