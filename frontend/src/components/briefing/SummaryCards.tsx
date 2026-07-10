// 报告摘要卡片组
// 展示报告关键指标：新闻数、资源量、价格、警告数

import { Newspaper, Database, DollarSign, AlertTriangle } from 'lucide-react';
import type { ReportSummary } from '@/types/briefing';
import { cn } from '@/lib/utils';

export interface SummaryCardsProps {
  summary: ReportSummary;
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  const cards = [
    {
      label: '新闻条数',
      value: summary.news_count,
      icon: Newspaper,
      tone: 'text-sky-400',
      available: summary.news_count > 0,
    },
    {
      label: '资源量数据',
      value: summary.resource_available ? '可用' : '缺失',
      icon: Database,
      tone: 'text-amber-400',
      available: summary.resource_available,
    },
    {
      label: '价格数据',
      value: summary.price_available ? '可用' : '缺失',
      icon: DollarSign,
      tone: 'text-emerald-400',
      available: summary.price_available,
    },
    {
      label: '警告数量',
      value: summary.warning_count,
      icon: AlertTriangle,
      tone: 'text-red-400',
      available: summary.warning_count === 0,
      invertAvailable: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {cards.map((c) => {
        const Icon = c.icon;
        const isOk = c.invertAvailable ? c.available : c.available;
        return (
          <div
            key={c.label}
            className="glass rounded-xl p-4 flex items-center gap-3"
          >
            <div
              className={cn(
                'w-9 h-9 rounded-lg flex items-center justify-center bg-white/[0.03]',
                c.tone,
              )}
            >
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] text-gray-500 uppercase tracking-wide">
                {c.label}
              </p>
              <p
                className={cn(
                  'text-lg font-semibold mt-0.5',
                  isOk ? 'text-gray-100' : 'text-gray-400',
                )}
              >
                {c.value}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
