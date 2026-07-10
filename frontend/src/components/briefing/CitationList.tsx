// 引用源列表
// 展示报告引用的新闻、PDF、价格数据源

import { Newspaper, FileText, DollarSign, Link2 } from 'lucide-react';
import type { Citation, CitationType } from '@/types/briefing';
import { Card, CardHeader } from '@/components/common/Card';
import { EmptyState } from '@/components/common/EmptyState';

const typeConfig: Record<
  CitationType,
  { icon: typeof Newspaper; tone: string; label: string }
> = {
  news: { icon: Newspaper, tone: 'text-sky-400', label: '新闻' },
  pdf: { icon: FileText, tone: 'text-amber-400', label: 'PDF' },
  price: { icon: DollarSign, tone: 'text-emerald-400', label: '价格源' },
  other: { icon: Link2, tone: 'text-gray-400', label: '其他' },
};

export interface CitationListProps {
  citations: Citation[];
}

export function CitationList({ citations }: CitationListProps) {
  return (
    <Card padding="md">
      <CardHeader
        title="引用源"
        subtitle={`共 ${citations.length} 条`}
        icon={<Link2 className="w-4 h-4" />}
      />

      {citations.length === 0 ? (
        <EmptyState title="暂无引用源" />
      ) : (
        <ul className="space-y-2">
          {citations.map((c, idx) => {
            const config = typeConfig[c.type] ?? typeConfig.other;
            const Icon = config.icon;
            const isLink = c.url && c.url !== '#';
            return (
              <li key={`${c.url}-${idx}`}>
                {isLink ? (
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-start gap-2.5 p-2 rounded-lg hover:bg-white/5 transition-colors group"
                  >
                    <Icon className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${config.tone}`} />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-gray-300 group-hover:text-gray-100 transition-colors truncate">
                        {c.title}
                      </p>
                      <p className="text-[10px] text-gray-600 truncate mt-0.5">
                        {c.url}
                      </p>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-500 border border-white/5 flex-shrink-0">
                      {config.label}
                    </span>
                  </a>
                ) : (
                  <div className="flex items-start gap-2.5 p-2">
                    <Icon className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${config.tone}`} />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-gray-400">{c.title}</p>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-500 border border-white/5 flex-shrink-0">
                      {config.label}
                    </span>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
