// 通用玻璃卡片组件
// 提供可复用的毛玻璃容器，支持 hover 高亮和内边距控制

import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** 是否启用 hover 高亮 */
  hoverable?: boolean;
  /** 内边距尺寸 */
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** 子节点 */
  children: ReactNode;
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-7',
};

export function Card({
  hoverable = false,
  padding = 'md',
  className,
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={cn(
        'glass rounded-xl',
        hoverable && 'glass-hover cursor-pointer',
        paddingClasses[padding],
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

/** 卡片标题区域 */
export function CardHeader({
  title,
  subtitle,
  icon,
  action,
  className,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex items-start justify-between mb-4', className)}>
      <div className="flex items-start gap-3">
        {icon && <div className="text-accent-light mt-0.5">{icon}</div>}
        <div>
          <h3 className="text-base font-semibold text-gray-100">{title}</h3>
          {subtitle && (
            <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
