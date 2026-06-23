import { useState } from 'react';
import { FileUpload } from '../components/FileUpload';
import { checkDissertation, type Report } from '../api/client';

interface UploadPageProps {
  onReportReady: (report: Report) => void;
}

const DOC_TYPES = [
  { value: 'thesis_humanities', label: 'Thesis — Humanities / Social Sciences' },
  { value: 'thesis_science', label: 'Thesis — Natural Sciences' },
  { value: 'project', label: 'Project / Coursework' },
];

export function UploadPage({ onReportReady }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('thesis_science');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const report = await checkDissertation(file, docType);
      onReportReady(report);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Failed to check document. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-[800px] px-6 pb-24 pt-12">
      <header className="mb-8">
        <h1 className="text-2xl font-medium text-[#202124]">
          Check Document Formatting
        </h1>
        <p className="mt-2 text-sm text-[#5f6368]">
          Upload your .docx dissertation to verify compliance with GOST 7.32-2017
        </p>
      </header>

      <section className="rounded-lg border border-[#dadce0] bg-white p-8 shadow-[0_1px_2px_0_rgba(60,64,67,.3),0_1px_3px_1px_rgba(60,64,67,.15)]">
        <div className="mb-6">
          <label
            htmlFor="doctype"
            className="mb-2 block text-sm font-medium text-[#202124]"
          >
            Document type
          </label>
          <div className="relative">
            <select
              id="doctype"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="w-full appearance-none rounded border border-[#dadce0] bg-white py-2.5 pl-3 pr-10 text-sm text-[#202124] hover:border-[#bdc1c6] focus:border-[#1a73e8] focus:outline-none"
            >
              {DOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
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
              className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5f6368]"
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </div>
        </div>

        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-[#202124]">
            Upload Document
          </label>
          <FileUpload onFileSelect={setFile} selectedFile={file} />
        </div>

        {error && (
          <div className="mb-6 flex items-start gap-2 rounded border border-[#fad2cf] bg-[#fce8e6] px-3 py-2.5 text-sm text-[#d93025]">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="mt-0.5 h-4 w-4 shrink-0"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-end">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!file || loading}
            className={`inline-flex items-center justify-center gap-2 rounded px-6 py-2.5 text-sm font-medium transition-colors ${
              !file || loading
                ? 'cursor-not-allowed bg-[#f1f3f4] text-[#9aa0a6]'
                : 'cursor-pointer bg-[#1a73e8] text-white hover:bg-[#1557b0] hover:shadow-md'
            }`}
          >
            {loading ? (
              <>
                <svg
                  className="h-4 w-4 animate-spin"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="3"
                    opacity="0.25"
                  />
                  <path
                    d="M22 12a10 10 0 0 1-10 10"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                </svg>
                <span>Checking…</span>
              </>
            ) : (
              <span>Check</span>
            )}
          </button>
        </div>
      </section>
    </div>
  );
}
