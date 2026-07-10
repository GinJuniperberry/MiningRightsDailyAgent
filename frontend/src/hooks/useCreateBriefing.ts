// 创建日报任务 Hook
// 调用 POST /api/briefings 并更新 store

import { useCallback, useState } from 'react';
import { briefingApi, ApiError } from '@/services/briefingApi';
import { useBriefingStore } from '@/store/briefingStore';

export interface UseCreateBriefingResult {
  /** 创建任务（成功后 store 进入 running 状态） */
  create: (query: string) => Promise<string | null>;
  /** 是否正在请求创建 */
  loading: boolean;
  /** 创建错误信息 */
  error: string | null;
}

export function useCreateBriefing(): UseCreateBriefingResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const startTask = useBriefingStore((s) => s.startTask);
  const setCreating = useBriefingStore((s) => s.setCreating);
  const setStoreError = useBriefingStore((s) => s.setError);

  const create = useCallback(
    async (query: string): Promise<string | null> => {
      const trimmed = query.trim();
      if (!trimmed) {
        setError('查询不能为空');
        return null;
      }

      setLoading(true);
      setError(null);
      setCreating();

      try {
        const res = await briefingApi.create(trimmed);
        startTask(res.task_id, trimmed);
        return res.task_id;
      } catch (err) {
        const message =
          err instanceof ApiError
            ? `创建失败：${err.message}`
            : err instanceof Error
              ? err.message
              : '未知错误';
        setError(message);
        setStoreError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [startTask, setCreating, setStoreError],
  );

  return { create, loading, error };
}
