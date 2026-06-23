import type { Report } from '../api/client';
import { ReportSummary } from '../components/ReportSummary';
import { IssueList } from '../components/IssueList';

interface ReportPageProps {
  report: Report;
  onBack: () => void;
}

export function ReportPage({ report, onBack }: ReportPageProps) {
  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${report.filename}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const checkedAt = new Date(report.checked_at);

  return (
    <div className="mx-auto w-full max-w-[960px] px-6 pb-24 pt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1 text-sm font-medium text-[#1a73e8] hover:text-[#1557b0] hover:underline"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-4 w-4"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
          Back
        </button>

        <button
          type="button"
          onClick={handleDownloadJson}
          className="inline-flex items-center gap-2 rounded border border-[#dadce0] bg-white px-4 py-1.5 text-sm font-medium text-[#1a73e8] hover:bg-[#f8f9fa]"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-4 w-4"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <path d="M7 10l5 5 5-5" />
            <path d="M12 15V3" />
          </svg>
          Export JSON
        </button>
      </div>

      <header className="mt-8 border-b border-[#e8eaed] pb-6">
        <h1 className="text-2xl font-medium text-[#202124]">Report</h1>
        <p className="mt-1 text-sm text-[#5f6368]">
          Generated{' '}
          <time dateTime={report.checked_at}>
            {checkedAt.toLocaleString(undefined, {
              dateStyle: 'long',
              timeStyle: 'short',
            })}
          </time>
        </p>
      </header>

      <div className="mt-8">
        <ReportSummary report={report} />
      </div>

      <div className="mt-10 mb-4 flex items-baseline gap-2">
        <h2 className="text-lg font-medium text-[#202124]">Issues</h2>
        <span className="text-sm text-[#5f6368]">({report.issues.length})</span>
      </div>

      <IssueList issues={report.issues} />
    </div>
  );
}
