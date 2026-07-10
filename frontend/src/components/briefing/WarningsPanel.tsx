// 警告面板
// 展示报告中累计的警告信息（数据降级、质检未过等）

import { AlertTriangle } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { cn } from '@/lib/utils';

export interface WarningsPanelProps {
  warnings: string[];
  className?: string;
}

export function WarningsPanel({ warnings, className }: WarningsPanelProps) {
  if (!warnings || warnings.length === 0) return null;

  return (
    <Card
      padding="md"
      className={cn('border-amber-500/20 bg-amber-500/[0.03]', className)}
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-amber-500/15 flex items-center justify-center flex-shrink-0">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-amber-300 mb-1.5">
            数据降级提示（{warnings.length}）
          </h4>
          <ul className="space-y-1">
            {warnings.map((w, idx) => (
              <li
                key={idx}
                className="text-xs text-amber-200/70 flex items-start gap-1.5"
              >
                <span className="text-amber-500/60 flex-shrink-0">·</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}
