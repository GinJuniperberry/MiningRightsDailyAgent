// 风险提示列表
// 兼容两种格式：字符串数组（当前后端默认）和结构化对象数组

import { Shield, ShieldAlert, AlertOctagon } from 'lucide-react';
import type { RiskItem } from '@/types/briefing';
import { Card, CardHeader } from '@/components/common/Card';
import { Badge, type BadgeTone } from '@/components/common/Badge';
import { EmptyState } from '@/components/common/EmptyState';

const levelConfig: Record<string, { tone: BadgeTone; label: string }> = {
  high: { tone: 'danger', label: '高风险' },
  medium: { tone: 'warning', label: '中风险' },
  low: { tone: 'success', label: '低风险' },
};

export interface RiskListProps {
  risks: RiskItem[];
}

export function RiskList({ risks }: RiskListProps) {
  return (
    <Card padding="md">
      <CardHeader
        title="风险提示"
        subtitle={`共 ${risks.length} 条`}
        icon={<Shield className="w-4 h-4" />}
      />

      {risks.length === 0 ? (
        <EmptyState title="暂无风险提示" description="本次未识别到显著风险" />
      ) : (
        <ul className="space-y-2.5">
          {risks.map((risk, idx) => {
            const isString = typeof risk === 'string';
            const title = isString ? `风险 ${idx + 1}` : risk.title;
            const description = isString ? risk : risk.description;
            const level = !isString && risk.level ? risk.level : 'medium';
            const config = levelConfig[level] ?? levelConfig.medium;
            const Icon = level === 'high' ? AlertOctagon : ShieldAlert;

            return (
              <li
                key={idx}
                className="p-3 rounded-lg bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-gray-400" />
                    <h4 className="text-sm font-medium text-gray-200">
                      {title}
                    </h4>
                  </div>
                  <Badge tone={config.tone}>{config.label}</Badge>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed pl-6">
                  {description}
                </p>
                {!isString && risk.mitigation && (
                  <div className="mt-2 pl-6 text-xs">
                    <span className="text-gray-500">应对建议：</span>
                    <span className="text-gray-300">{risk.mitigation}</span>
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
