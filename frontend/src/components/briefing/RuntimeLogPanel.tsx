// 运行时事件日志面板
// 展示 SSE 推送的所有事件，支持自动滚动到底部

import { useEffect, useRef } from 'react';
import {
  Check,
  AlertTriangle,
  Play,
  Flag,
  XCircle,
  Terminal,
} from 'lucide-react';
import { useBriefingStore } from '@/store/briefingStore';
import type { NodeEvent, NodeEventType } from '@/types/briefing';
import { getNodeLabel } from '@/lib/nodeFlow';
import { cn } from '@/lib/utils';

const eventTypeConfig: Record<
  NodeEventType,
  { icon: typeof Check; tone: string }
> = {
  node_start: { icon: Play, tone: 'text-sky-400' },
  node_success: { icon: Check, tone: 'text-emerald-400' },
  node_warning: { icon: AlertTriangle, tone: 'text-amber-400' },
  task_done: { icon: Flag, tone: 'text-accent-light' },
  task_failed: { icon: XCircle, tone: 'text-red-400' },
};

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  } catch {
    return '--:--:--';
  }
}

export function RuntimeLogPanel() {
  const events = useBriefingStore((s) => s.events);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 新事件时自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="glass rounded-xl overflow-hidden flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-accent-light" />
          <span className="text-sm font-medium text-gray-200">运行日志</span>
        </div>
        <span className="text-xs text-gray-500">{events.length} 条</span>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-3 font-mono text-xs space-y-1 min-h-[200px] max-h-[480px]"
      >
        {events.length === 0 ? (
          <div className="text-gray-600 italic py-4 text-center">
            等待事件...
          </div>
        ) : (
          events.map((event: NodeEvent, idx: number) => {
            const config = eventTypeConfig[event.type];
            const Icon = config.icon;
            const nodeLabel = event.node ? getNodeLabel(event.node) : '';
            return (
              <div
                key={`${event.timestamp}-${idx}`}
                className="flex items-start gap-2 animate-fade-in"
              >
                <span className="text-gray-600 flex-shrink-0">
                  {formatTime(event.timestamp)}
                </span>
                <Icon className={cn('w-3.5 h-3.5 flex-shrink-0 mt-0.5', config.tone)} />
                {nodeLabel && (
                  <span className="text-accent-light/80 flex-shrink-0">
                    [{nodeLabel}]
                  </span>
                )}
                <span className="text-gray-300 break-all">{event.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
