// LangGraph 节点流程可视化
// 纵向时间线展示 14 个节点的执行状态

import { Check, Circle, AlertTriangle, Loader } from 'lucide-react';
import { useBriefingStore } from '@/store/briefingStore';
import { NODE_FLOW, isConditionalNode } from '@/lib/nodeFlow';
import type { NodeRunStatus } from '@/types/briefing';
import { cn } from '@/lib/utils';

const statusConfig: Record<
  NodeRunStatus,
  { icon: typeof Check; tone: string; label: string }
> = {
  pending: {
    icon: Circle,
    tone: 'text-gray-600 border-gray-700',
    label: '等待中',
  },
  running: {
    icon: Loader,
    tone: 'text-accent-light border-accent animate-breathe',
    label: '执行中',
  },
  success: {
    icon: Check,
    tone: 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10',
    label: '完成',
  },
  warning: {
    icon: AlertTriangle,
    tone: 'text-amber-400 border-amber-500/50 bg-amber-500/10',
    label: '降级',
  },
  skipped: {
    icon: Circle,
    tone: 'text-gray-700 border-gray-800',
    label: '跳过',
  },
};

export function GraphProgress() {
  const nodes = useBriefingStore((s) => s.nodes);
  const status = useBriefingStore((s) => s.status);

  // 任务完成后，将未执行的节点标记为 skipped
  const isFinished = status === 'success' || status === 'failed';

  return (
    <div className="relative">
      {/* 纵向连接线 */}
      <div
        className="absolute left-[15px] top-2 bottom-2 w-px bg-gradient-to-b from-transparent via-white/10 to-transparent"
        aria-hidden="true"
      />

      <ol className="space-y-1">
        {NODE_FLOW.map((node, idx) => {
          const info = nodes[node.name];
          if (!info) return null;

          // 任务结束后，未执行的节点视为跳过
          const effectiveStatus: NodeRunStatus =
            isFinished && info.status === 'pending' ? 'skipped' : info.status;
          const config = statusConfig[effectiveStatus];
          const Icon = config.icon;
          const isConditional = isConditionalNode(node.name);
          const dimmed = effectiveStatus === 'pending' || effectiveStatus === 'skipped';

          return (
            <li
              key={node.name}
              className={cn(
                'relative flex items-start gap-3 pl-0 py-1.5 animate-slide-up',
              )}
              style={{ animationDelay: `${idx * 30}ms` }}
            >
              <div
                className={cn(
                  'relative z-10 flex-shrink-0 w-8 h-8 rounded-full border-2 bg-base-900',
                  'flex items-center justify-center transition-all',
                  config.tone,
                )}
              >
                <Icon
                  className={cn(
                    'w-3.5 h-3.5',
                    effectiveStatus === 'running' && 'animate-spin',
                  )}
                />
              </div>

              <div
                className={cn(
                  'flex-1 min-w-0 pt-1',
                  dimmed && 'opacity-50',
                )}
              >
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium text-gray-200">
                    {node.label}
                  </span>
                  {isConditional && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-500 border border-white/5">
                      条件分支
                    </span>
                  )}
                  {effectiveStatus !== 'pending' && (
                    <span className="text-[10px] text-gray-500">
                      {config.label}
                    </span>
                  )}
                </div>
                {info.message && effectiveStatus !== 'pending' && (
                  <p
                    className={cn(
                      'text-xs mt-0.5 truncate',
                      effectiveStatus === 'warning'
                        ? 'text-amber-300/80'
                        : 'text-gray-500',
                    )}
                    title={info.message}
                  >
                    {info.message}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
