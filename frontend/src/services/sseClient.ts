// SSE 事件流客户端
// 监听后端 GET /api/briefings/{task_id}/events

import type { NodeEvent } from '@/types/briefing';

export type SseEventHandler = (event: NodeEvent) => void;
export type SseErrorHandler = (error: Event) => void;
export type SseOpenHandler = () => void;

export interface SseClientOptions {
  taskId: string;
  onEvent: SseEventHandler;
  onError?: SseErrorHandler;
  onOpen?: SseOpenHandler;
}

export interface SseClient {
  /** 关闭 SSE 连接 */
  close: () => void;
  /** 当前是否已连接 */
  readonly readyState: number;
}

/**
 * 创建 SSE 客户端
 *
 * 浏览器原生 EventSource 自动处理重连，无需额外逻辑。
 * 后端会在任务结束后关闭流，EventSource 收到关闭后会触发 onerror。
 * 调用方需要根据事件流中的 task_done / task_failed 事件判断任务是否结束。
 */
export function createSseClient(options: SseClientOptions): SseClient {
  const { taskId, onEvent, onError, onOpen } = options;
  const url = `/api/briefings/${taskId}/events`;

  const source = new EventSource(url, { withCredentials: false });

  source.onopen = () => {
    onOpen?.();
  };

  source.onmessage = (e: MessageEvent) => {
    // 心跳注释不会触发 onmessage，但 data 为空时跳过
    if (!e.data || e.data.trim() === '') return;
    try {
      const event = JSON.parse(e.data) as NodeEvent;
      onEvent(event);
    } catch (err) {
      console.error('[SSE] 解析失败:', err, e.data);
    }
  };

  source.onerror = (e) => {
    onError?.(e);
  };

  return {
    close: () => {
      source.close();
    },
    get readyState() {
      return source.readyState;
    },
  };
}
