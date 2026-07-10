// 加载指示器组件
// 提供 spinner 与点状两种风格

import { cn } from '@/lib/utils';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-10 w-10',
};

export function LoadingSpinner({
  size = 'md',
  className,
  label,
}: LoadingSpinnerProps) {
  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      <svg
        className={cn('animate-spin text-accent', sizeMap[size])}
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="3"
        />
        <path
          className="opacity-90"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v3a5 5 0 00-5 5H4z"
        />
      </svg>
      {label && <span className="text-sm text-gray-400">{label}</span>}
    </div>
  );
}

/** 全屏加载遮罩 */
export function FullScreenLoader({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <LoadingSpinner size="lg" />
      {label && <p className="text-gray-400 text-sm">{label}</p>}
    </div>
  );
}

/** 三点跳动加载 */
export function DotLoader({ className }: { className?: string }) {
  return (
    <div className={cn('inline-flex items-center gap-1', className)}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-accent animate-breathe"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}
