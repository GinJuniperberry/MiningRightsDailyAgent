// 空状态占位组件

import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-6 text-center',
        className,
      )}
    >
      {icon && (
        <div className="text-gray-600 mb-3" aria-hidden="true">
          {icon}
        </div>
      )}
      <p className="text-gray-300 text-sm font-medium">{title}</p>
      {description && (
        <p className="text-gray-500 text-xs mt-1.5 max-w-xs">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
