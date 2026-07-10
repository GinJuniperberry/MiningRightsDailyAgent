// 资源量数据表格
// 展示 extract_resources 节点抽取的结构化资源数据

import { Database, ExternalLink } from 'lucide-react';
import type { ResourceItem, Quantity } from '@/types/briefing';
import { Card, CardHeader } from '@/components/common/Card';
import { EmptyState } from '@/components/common/EmptyState';
import { Badge } from '@/components/common/Badge';

export interface ResourceTableProps {
  resources: ResourceItem[];
  reportUrl?: string;
}

function formatQuantity(q?: Quantity): string {
  if (!q) return '-';
  return `${q.value} ${q.unit}`;
}

function formatConfidence(c?: number): string {
  if (c == null) return '-';
  return `${(c * 100).toFixed(0)}%`;
}

export function ResourceTable({ resources, reportUrl }: ResourceTableProps) {
  return (
    <Card padding="md">
      <CardHeader
        title="资源量数据"
        subtitle="来自 JORC / NI-43-101 报告"
        icon={<Database className="w-4 h-4" />}
        action={
          reportUrl && reportUrl !== '#' ? (
            <a
              href={reportUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-accent-light hover:text-accent transition-colors"
            >
              查看原报告
              <ExternalLink className="w-3 h-3" />
            </a>
          ) : undefined
        }
      />

      {resources.length === 0 ? (
        <EmptyState
          title="暂无资源量数据"
          description="本次未抽取到结构化资源量，可能需要人工复核"
        />
      ) : (
        <div className="overflow-x-auto -mx-2">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-500">
                <th className="px-2 py-2 font-medium">类别</th>
                <th className="px-2 py-2 font-medium">矿石量</th>
                <th className="px-2 py-2 font-medium">品位</th>
                <th className="px-2 py-2 font-medium">金属量</th>
                <th className="px-2 py-2 font-medium">置信度</th>
              </tr>
            </thead>
            <tbody>
              {resources.map((r, idx) => (
                <tr
                  key={`${r.category}-${idx}`}
                  className="border-t border-white/5 hover:bg-accent/5 transition-colors"
                >
                  <td className="px-2 py-2.5 text-gray-200 font-medium">
                    {r.category}
                  </td>
                  <td className="px-2 py-2.5 text-gray-300 font-mono">
                    {formatQuantity(r.ore_tonnage)}
                  </td>
                  <td className="px-2 py-2.5 text-gray-300 font-mono">
                    {formatQuantity(r.grade)}
                  </td>
                  <td className="px-2 py-2.5 text-gray-300 font-mono">
                    {formatQuantity(r.contained_metal)}
                  </td>
                  <td className="px-2 py-2.5">
                    {r.confidence != null && r.confidence >= 0.85 ? (
                      <Badge tone="success">{formatConfidence(r.confidence)}</Badge>
                    ) : r.confidence != null ? (
                      <Badge tone="warning">{formatConfidence(r.confidence)}</Badge>
                    ) : (
                      <span className="text-gray-600">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
