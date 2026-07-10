// Markdown 报告渲染组件
// 使用 react-markdown + remark-gfm，配合 .markdown-body 样式

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText } from 'lucide-react';

export interface MarkdownReportProps {
  markdown: string;
  /** 标题（可选，显示在顶部） */
  title?: string;
}

export function MarkdownReport({ markdown, title }: MarkdownReportProps) {
  return (
    <div className="glass rounded-xl p-6">
      {title && (
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-white/5">
          <FileText className="w-4 h-4 text-accent-light" />
          <h3 className="text-base font-semibold text-gray-100">{title}</h3>
        </div>
      )}
      <div className="markdown-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown || '*暂无报告内容*'}</ReactMarkdown>
      </div>
    </div>
  );
}
