import type { Issue } from '../api/client';

interface IssueCardProps {
  issue: Issue;
}

interface SeverityMeta {
  label: string;
  accent: string;
  pillBg: string;
  pillText: string;
}

const SEVERITY_META: Record<string, SeverityMeta> = {
  error: {
    label: 'Error',
    accent: '#d93025',
    pillBg: '#fce8e6',
    pillText: '#c5221f',
  },
  warning: {
    label: 'Warning',
    accent: '#f9ab00',
    pillBg: '#feefc3',
    pillText: '#b06000',
  },
  info: {
    label: 'Info',
    accent: '#1a73e8',
    pillBg: '#e8f0fe',
    pillText: '#1967d2',
  },
};

export function IssueCard({ issue }: IssueCardProps) {
  const meta = SEVERITY_META[issue.severity] || SEVERITY_META.info;

  return (
    <article
      className="relative mb-2 rounded-lg border border-[#dadce0] bg-white p-4 pl-5"
      style={{ borderLeft: `3px solid ${meta.accent}` }}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span
          className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium"
          style={{ background: meta.pillBg, color: meta.pillText }}
        >
          {meta.label}
        </span>
        <span className="text-xs text-[#5f6368]">{issue.category}</span>
        {issue.rule_ref && (
          <span className="font-mono text-xs text-[#5f6368]">
            §&nbsp;{issue.rule_ref}
          </span>
        )}
        {issue.location?.section_name && (
          <span className="ml-auto text-xs text-[#5f6368]">
            {issue.location.section_name}
          </span>
        )}
      </div>

      <p className="mt-2 text-sm font-medium text-[#202124]">{issue.message}</p>

      {issue.suggestion && (
        <p className="mt-1 text-sm text-[#5f6368]">{issue.suggestion}</p>
      )}

      {issue.location?.context_text && (
        <div className="mt-3 rounded bg-[#f8f9fa] px-3 py-2">
          <div className="flex items-center justify-between text-xs text-[#5f6368]">
            <span>Context</span>
            {typeof issue.location.paragraph_index === 'number' && (
              <span className="font-mono">
                ¶ {issue.location.paragraph_index}
              </span>
            )}
          </div>
          <p className="mt-1 font-mono text-xs leading-relaxed text-[#3c4043] line-clamp-3">
            {issue.location.context_text}
          </p>
        </div>
      )}
    </article>
  );
}
