// 获取报告详情 Hook
// 调用 GET /api/briefings/{task_id}

import { useCallback, useEffect, useState } from 'react';
import {
  briefingApi,
  ApiError,
  TaskRunningError,
} from '@/services/briefingApi';
import type { ReportDetail } from '@/types/briefing';

export interface UseBriefingReportResult {
  report: ReportDetail | null;
  loading: boolean;
  error: string | null;
  /** 重新拉取 */
  refetch: () => void;
}

/**
 * 获取报告详情
 *
 * - taskId 为 null 时不请求
 * - 若任务仍在执行（HTTP 202），不视为错误，仅返回 loading=false 且 report=null
 * - 任务完成后再次调用可获取完整报告
 */
export function useBriefingReport(taskId: string | null): UseBriefingReportResult {
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refetchFlag, setRefetchFlag] = useState(0);

  const refetch = useCallback(() => setRefetchFlag((n) => n + 1), []);

  useEffect(() => {
    if (!taskId) {
      setReport(null);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    briefingApi
      .getReport(taskId)
      .then((data) => {
        if (!cancelled) {
          setReport(data);
        }
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof TaskRunningError) {
          // 任务仍在执行，不算错误
          setReport(null);
        } else if (err instanceof ApiError) {
          setError(`获取报告失败：${err.message}`);
        } else if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('未知错误');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [taskId, refetchFlag]);

  return { report, loading, error, refetch };
}
