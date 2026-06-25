import { useDropzone } from 'react-dropzone';
import { useCallback } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1);
  return `${(bytes / Math.pow(k, i)).toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
}

export function FileUpload({ onFileSelect, selectedFile }: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) onFileSelect(acceptedFiles[0]);
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
  });

  const stateClasses = isDragReject
    ? 'border-[#d93025] bg-[#fce8e6]'
    : isDragActive
    ? 'border-[#1a73e8] bg-blue-50'
    : selectedFile
    ? 'border-[#1e8e3e] bg-[#e6f4ea]'
    : 'border-[#dadce0] bg-white hover:border-[#bdc1c6] hover:bg-[#f8f9fa]';

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-lg border border-dashed px-8 py-10 text-center transition-colors ${stateClasses}`}
    >
      <input {...getInputProps()} />

      {selectedFile ? (
        <div className="flex flex-col items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-[#1e8e3e] ring-1 ring-[#ceead6]">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </div>
          <p className="text-sm font-medium text-[#1e8e3e] break-all">
            {selectedFile.name}
          </p>
          <p className="text-xs text-[#5f6368]">
            {formatBytes(selectedFile.size)} · Click to replace
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-8 w-8 text-[#5f6368]"
            aria-hidden
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <path d="M17 8l-5-5-5 5" />
            <path d="M12 3v12" />
          </svg>
          <p className="text-sm text-[#202124]">
            {isDragActive
              ? 'Drop the file here'
              : 'Drag and drop a .docx file here'}
          </p>
          <p className="text-xs text-[#1a73e8]">or click to browse</p>
          <p className="mt-1 text-xs text-[#5f6368]">
            Accepts .docx files up to 50 MB
          </p>
        </div>
      )}
    </div>
  );
}
