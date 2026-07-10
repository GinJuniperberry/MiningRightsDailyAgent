// Zustand 全局状态：当前日报任务的执行进度与事件日志

import { create } from 'zustand';
import type {
  BriefingStatus,
  NodeEvent,
  NodeRunInfo,
  NodeRunStatus,
} from '@/types/briefing';
import { NODE_FLOW } from '@/lib/nodeFlow';

/** 构建初始节点状态映射 */
function makeInitialNodes(): Record<string, NodeRunInfo> {
  const map: Record<string, NodeRunInfo> = {};
  for (const node of NODE_FLOW) {
    map[node.name] = {
      name: node.name,
      label: node.label,
      status: 'pending',
    };
  }
  // expand_news_days 是 search_news 的条件分支，也加入（但不在主流程展示）
  map['expand_news_days'] = {
    name: 'expand_news_days',
    label: '扩大搜索范围',
    status: 'pending',
  };
  return map;
}

interface BriefingState {
  /** 当前任务 ID */
  taskId: string | null;
  /** 用户输入的查询 */
  query: string;
  /** 任务综合状态 */
  status: BriefingStatus;
  /** 节点执行信息映射 */
  nodes: Record<string, NodeRunInfo>;
  /** 事件日志（按时间顺序） */
  events: NodeEvent[];
  /** 错误信息 */
  error: string | null;

  /** 设置为创建中状态 */
  setCreating: () => void;
  /** 任务创建成功，进入 running 状态 */
  startTask: (taskId: string, query: string) => void;
  /** 设置错误 */
  setError: (err: string | null) => void;
  /** 应用一个 SSE 事件 */
  applyEvent: (event: NodeEvent) => void;
  /** 重置整个 store（返回首页时调用） */
  reset: () => void;
}

export const useBriefingStore = create<BriefingState>((set) => ({
  taskId: null,
  query: '',
  status: 'idle',
  nodes: makeInitialNodes(),
  events: [],
  error: null,

  setCreating: () => set({ status: 'creating', error: null }),

  startTask: (taskId, query) =>
    set({
      taskId,
      query,
      status: 'running',
      nodes: makeInitialNodes(),
      events: [],
      error: null,
    }),

  setError: (err) =>
    set({ error: err, status: err ? 'failed' : 'idle' }),

  applyEvent: (event) =>
    set((state) => {
      const newEvents = [...state.events, event];
      const newNodes = { ...state.nodes };

      // 更新对应节点状态
      if (event.node && newNodes[event.node]) {
        const node: NodeRunInfo = { ...newNodes[event.node] };

        switch (event.type) {
          case 'node_start':
            node.status = 'running' as NodeRunStatus;
            node.startedAt = event.timestamp;
            node.message = event.message;
            break;
          case 'node_success':
            // 若之前已有 warning，保留 warning 状态（更严重）
            if (node.status !== 'warning') {
              node.status = 'success';
            }
            node.finishedAt = event.timestamp;
            node.message = event.message;
            node.payload = event.payload;
            break;
          case 'node_warning':
            node.status = 'warning';
            node.message = event.message;
            break;
        }

        newNodes[event.node] = node;
      }

      // 更新任务状态
      let newStatus = state.status;
      if (event.type === 'task_done') {
        newStatus = 'success';
      } else if (event.type === 'task_failed') {
        newStatus = 'failed';
      }

      return { events: newEvents, nodes: newNodes, status: newStatus };
    }),

  reset: () =>
    set({
      taskId: null,
      query: '',
      status: 'idle',
      nodes: makeInitialNodes(),
      events: [],
      error: null,
    }),
}));
