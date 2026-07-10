// 新闻列表组件
// 展示 search_news / fetch_articles 节点输出的新闻条目

import { Newspaper, ExternalLink, Clock, AlertTriangle } from 'lucide-react';
import type { NewsItem } from '@/types/briefing';
import { Card, CardHeader } from '@/components/common/Card';
import { EmptyState } from '@/components/common/EmptyState';

function formatDate(iso?: string): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
    });
  } catch {
    return '';
  }
}

export interface NewsListProps {
  news: NewsItem[];
  /** 最多展示条数 */
  limit?: number;
}

export function NewsList({ news, limit }: NewsListProps) {
  const items = limit ? news.slice(0, limit) : news;

  return (
    <Card padding="md">
      <CardHeader
        title="相关新闻"
        subtitle={`共 ${news.length} 条`}
        icon={<Newspaper className="w-4 h-4" />}
      />

      {items.length === 0 ? (
        <EmptyState title="暂无相关新闻" />
      ) : (
        <ul className="space-y-2.5">
          {items.map((n, idx) => {
            const isLink = !!n.url;
            const content = (
              <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors group">
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors line-clamp-2">
                      {n.title}
                    </h4>
                    {isLink && (
                      <ExternalLink className="w-3 h-3 text-gray-600 group-hover:text-accent-light flex-shrink-0 mt-1 transition-colors" />
                    )}
                  </div>
                  {(n.summary || n.content) && (
                    <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                      {n.summary || n.content}
                    </p>
                  )}
                  {n.warning && (
                    <p className="text-[10px] text-amber-400/70 mt-1 flex items-center gap-1">
                      <AlertTriangle className="w-2.5 h-2.5" />
                      {n.warning}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-1.5 text-[10px] text-gray-500">
                    {n.source && <span>{n.source}</span>}
                    {(n.published || n.published_at) && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-2.5 h-2.5" />
                        {formatDate(n.published || n.published_at)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );

            return (
              <li key={idx}>
                {isLink ? (
                  <a
                    href={n.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block"
                  >
                    {content}
                  </a>
                ) : (
                  content
                )}
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
