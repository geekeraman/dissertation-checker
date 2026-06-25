import { useState } from 'react';
import type { ReactNode } from 'react';
import { UploadPage } from './pages/UploadPage';
import { ReportPage } from './pages/ReportPage';
import type { Report } from './api/client';

function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-full bg-white">
      <header className="sticky top-0 z-20 border-b border-[#dadce0] bg-white">
        <div className="mx-auto flex h-16 w-full max-w-[1200px] items-center px-6">
          <a href="/" className="inline-flex items-center gap-3">
            <span
              aria-hidden
              className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1a73e8] text-white"
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
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6" />
                <path d="m9 15 2 2 4-4" />
              </svg>
            </span>
            <span className="text-lg font-medium text-[#202124]">
              Dissertation Format Checker
            </span>
          </a>
        </div>
      </header>

      <main>{children}</main>
    </div>
  );
}

function App() {
  const [report, setReport] = useState<Report | null>(null);

  return (
    <AppShell>
      {report ? (
        <ReportPage report={report} onBack={() => setReport(null)} />
      ) : (
        <UploadPage onReportReady={setReport} />
      )}
    </AppShell>
  );
}

export default App;
