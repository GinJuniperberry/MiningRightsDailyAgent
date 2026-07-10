// 价格趋势信息卡片
// 展示最新价、涨跌幅、均线 + 文字观测摘要
// 注意：后端 observations 是字符串数组（文字描述），不是时序数据点

import { TrendingUp, TrendingDown, Minus, BarChart3, Lightbulb } from 'lucide-react';
import type { PriceInfo } from '@/types/briefing';
import { Card, CardHeader } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { cn } from '@/lib/utils';

export interface PriceTrendChartProps {
  price: PriceInfo;
}

const trendConfig = {
  up: { icon: TrendingUp, tone: 'text-emerald-400' as const, label: '上升', badge: 'success' as const },
  down: { icon: TrendingDown, tone: 'text-red-400' as const, label: '下降', badge: 'danger' as const },
  flat: { icon: Minus, tone: 'text-gray-400' as const, label: '平稳', badge: 'muted' as const },
};

export function PriceTrendChart({ price }: PriceTrendChartProps) {
  const trend = trendConfig[price.trend] ?? trendConfig.flat;
  const TrendIcon = trend.icon;

  const stats = [
    { label: '最新价', value: `${price.latest_price.toLocaleString()} ${price.unit}`, highlight: true },
    {
      label: '涨跌幅',
      value: `${price.change_pct > 0 ? '+' : ''}${price.change_pct}%`,
      tone: price.change_pct > 0 ? 'text-emerald-400' : price.change_pct < 0 ? 'text-red-400' : 'text-gray-400',
    },
    { label: 'MA7', value: `${price.ma_7.toLocaleString()} ${price.unit}` },
    { label: 'MA30', value: `${price.ma_30.toLocaleString()} ${price.unit}` },
  ];

  return (
    <Card padding="md">
      <CardHeader
        title="价格行情"
        subtitle={`${price.commodity || '商品'} · 近 30 日趋势`}
        icon={<TrendIcon className={cn('w-4 h-4', trend.tone)} />}
        action={
          <Badge tone={trend.badge} dot>
            {trend.label}
          </Badge>
        }
      />

      {/* 关键指标 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
        {stats.map((s) => (
          <div key={s.label} className="bg-white/[0.03] rounded-lg p-2.5">
            <p className="text-[10px] text-gray-500 mb-1">{s.label}</p>
            <p
              className={cn(
                'text-sm font-mono font-medium',
                s.highlight && 'text-accent-light',
                s.tone,
                !s.highlight && !s.tone && 'text-gray-300',
              )}
            >
              {s.value}
            </p>
          </div>
        ))}
      </div>

      {/* 价格趋势可视化条 */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1.5">
          <span>MA30: {price.ma_30.toLocaleString()}</span>
          <span>MA7: {price.ma_7.toLocaleString()}</span>
          <span>当前: {price.latest_price.toLocaleString()}</span>
        </div>
        <div className="relative h-2 rounded-full bg-white/5 overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-accent/40 to-accent rounded-full"
            style={{
              width: `${Math.min(100, Math.max(20, (price.latest_price / Math.max(price.ma_30, price.latest_price, 1)) * 100))}%`,
            }}
          />
        </div>
      </div>

      {/* 观测摘要 */}
      {price.observations && price.observations.length > 0 && (
        <div className="bg-white/[0.02] rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs font-medium text-gray-300">趋势观测</span>
          </div>
          <ul className="space-y-1.5">
            {price.observations.map((obs, idx) => (
              <li
                key={idx}
                className="text-xs text-gray-400 flex items-start gap-1.5"
              >
                <BarChart3 className="w-3 h-3 text-accent/60 flex-shrink-0 mt-0.5" />
                <span>{obs}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
