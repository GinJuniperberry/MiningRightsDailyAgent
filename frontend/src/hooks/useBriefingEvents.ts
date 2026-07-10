// SSE 事件订阅 Hook
// 监听 GET /api/briefings/{task_id}/events，将事件应用到 store

import { useEffect, useRef } from 'react';
import { createSseClient, type SseClient } from '@/services/sseClient';
import { useBriefingStore } from '@/store/briefingStore';
import type { NodeEvent } from '@/types/briefing';

export interface UseBriefingEventsOptions {
  /** 任务 ID，为 null 时不订阅 */
  taskId: string | null;
  /** 任务结束回调（success 或 failed） */
  onDone?: (status: 'success' | 'failed') => void;
  /** 启用/禁用订阅 */
  enabled?: boolean;
}

/**
 * 订阅指定任务的 SSE 事件流
 *
 * - 自动在 taskId 变化或组件卸载时关闭旧连接
 * - 收到 task_done / task_failed 后自动关闭连接
 * - EventSource 自动重连，但若任务已结束则不重连
 */
export function useBriefingEvents({
  taskId,
  onDone,
  enabled = true,
}: UseBriefingEventsOptions) {
  const clientRef = useRef<SseClient | null>(null);
  const applyEvent = useBriefingStore((s) => s.applyEvent);
  const onDoneRef = useRef(onDone);
  onDoneRef.current = onDone;

  useEffect(() => {
    if (!enabled || !taskId) {
      return;
    }

    let closed = false;

    const client = createSseClient({
      taskId,
      onEvent: (event: NodeEvent) => {
        applyEvent(event);

        if (event.type === 'task_done') {
          if (!closed) {
            closed = true;
            // 等待 store 更新后再回调
            setTimeout(() => onDoneRef.current?.('success'), 0);
            client.close();
          }
        } else if (event.type === 'task_failed') {
          if (!closed) {
            closed = true;
            setTimeout(() => onDoneRef.current?.('failed'), 0);
            client.close();
          }
        }
      },
      onError: () => {
        // EventSource 自动重连，无需手动处理
        // 但若 readyState 为 CLOSED（2）且任务未完成，说明连接彻底断开
        // 这里交给上层组件判断 store.status 决定是否重试
      },
    });

    clientRef.current = client;

    return () => {
      closed = true;
      client.close();
      clientRef.current = null;
    };
  }, [taskId, enabled, applyEvent]);

  return clientRef;
}
