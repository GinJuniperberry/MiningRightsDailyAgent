// 状态徽章组件
// 用于节点状态、任务状态、风险等级等的可视化标记

import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type BadgeTone =
  | 'default'
  | 'accent'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'muted';

export interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
  className?: string;
  dot?: boolean;
}

const toneClasses: Record<BadgeTone, string> = {
  default: 'bg-white/5 text-gray-300 border-white/10',
  accent: 'bg-accent/15 text-accent-light border-accent/30',
  success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  warning: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  danger: 'bg-red-500/15 text-red-300 border-red-500/30',
  info: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
  muted: 'bg-white/5 text-gray-500 border-white/5',
};

const dotClasses: Record<BadgeTone, string> = {
  default: 'bg-gray-400',
  accent: 'bg-accent',
  success: 'bg-emerald-400',
  warning: 'bg-amber-400',
  danger: 'bg-red-400',
  info: 'bg-sky-400',
  muted: 'bg-gray-500',
};

export function Badge({
  tone = 'default',
  children,
  className,
  dot = false,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full',
        'text-xs font-medium border',
        toneClasses[tone],
        className,
      )}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full',
            tone === 'accent' && 'animate-breathe',
            dotClasses[tone],
          )}
        />
      )}
      {children}
    </span>
  );
}
