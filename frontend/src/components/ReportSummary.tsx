import type { Report } from '../api/client';

interface ReportSummaryProps {
  report: Report;
}

const DOC_TYPE_LABEL: Record<string, string> = {
  thesis_humanities: 'Thesis · Humanities',
  thesis_science: 'Thesis · Natural Sciences',
  project: 'Project / Coursework',
};

const SEVERITY_DOT: Record<string, string> = {
  error: '#d93025',
  warning: '#f9ab00',
  info: '#1a73e8',
};

export function ReportSummary({ report }: ReportSummaryProps) {
  const noIssues = report.total_issues === 0;
  const errorCount = report.issues_by_severity?.error ?? 0;
  const warningCount = report.issues_by_severity?.warning ?? 0;
  const infoCount = report.issues_by_severity?.info ?? 0;

  return (
    <section className="rounded-lg bg-white shadow-[0_1px_2px_0_rgba(60,64,67,.3),0_1px_3px_1px_rgba(60,64,67,.15)]">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e8eaed] px-6 py-4">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-[#202124]">
            {report.filename}
          </p>
          <p className="mt-0.5 text-xs text-[#5f6368]">
            {DOC_TYPE_LABEL[report.doc_type] || report.doc_type}
          </p>
        </div>
        <p className="font-mono text-xs text-[#5f6368]">
          ID #{report.id.slice(0, 8)}
        </p>
      </div>

      {noIssues ? (
        <div className="flex items-center gap-3 px-6 py-8">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#e6f4ea]">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="#1e8e3e"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </div>
          <div>
            <p className="text-base font-medium text-[#1e8e3e]">
              No issues found
            </p>
            <p className="mt-0.5 text-sm text-[#5f6368]">
              Your document passes every check in this rubric.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-3 divide-x divide-[#e8eaed]">
          <Metric
            value={errorCount}
            label="Errors"
            valueColor="text-[#d93025]"
          />
          <Metric
            value={warningCount}
            label="Warnings"
            valueColor="text-[#f9ab00]"
          />
          <Metric
            value={infoCount}
            label="Info"
            valueColor="text-[#1a73e8]"
          />
        </div>
      )}

      {Object.keys(report.issues_by_category || {}).length > 0 && (
        <div className="border-t border-[#e8eaed] px-6 py-5">
          <p className="mb-3 text-xs font-medium uppercase tracking-wide text-[#5f6368]">
            By category
          </p>
          <ul className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
            {Object.entries(report.issues_by_category).map(([cat, count]) => (
              <li
                key={cat}
                className="flex items-center justify-between gap-3 text-sm text-[#202124]"
              >
                <span className="inline-flex items-center gap-2 min-w-0">
                  <span
                    className="h-1.5 w-1.5 shrink-0 rounded-full"
                    style={{ background: SEVERITY_DOT.info }}
                  />
                  <span className="truncate">{cat}</span>
                </span>
                <span className="font-medium text-[#5f6368]">{count}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function Metric({
  value,
  label,
  valueColor,
}: {
  value: number;
  label: string;
  valueColor: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-6">
      <span className={`text-2xl font-medium leading-none ${valueColor}`}>
        {value}
      </span>
      <span className="mt-2 text-xs text-[#5f6368]">{label}</span>
    </div>
  );
}
