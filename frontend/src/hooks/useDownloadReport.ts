// 下载报告 Hook
// 调用 GET /api/briefings/{task_id}/download，触发浏览器下载

import { useCallback, useState } from 'react';
import { briefingApi, ApiError } from '@/services/briefingApi';

export interface UseDownloadReportResult {
  /** 触发下载 */
  download: (taskId: string, filename?: string) => Promise<void>;
  /** 是否正在下载 */
  loading: boolean;
  /** 错误信息 */
  error: string | null;
}

/**
 * 下载 Markdown 报告
 *
 * 使用 Blob + URL.createObjectURL 触发浏览器下载，
 * 避免直接打开链接导致导航跳转。
 */
export function useDownloadReport(): UseDownloadReportResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const download = useCallback(async (taskId: string, filename?: string) => {
    setLoading(true);
    setError(null);

    try {
      const blob = await briefingApi.download(taskId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `briefing_${taskId}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      // 释放 URL 对象
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? `下载失败：${err.message}`
          : err instanceof Error
            ? err.message
            : '未知错误';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { download, loading, error };
}
