// 矿权日报 REST API 客户端
// 封装后端 /api/briefings 系列接口

import type {
  CreateBriefingResponse,
  ReportDetail,
  BriefingListResponse,
} from '@/types/briefing';

const API_BASE = '/api';

/** API 错误 */
export class ApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

/** 任务仍在执行中（HTTP 202） */
export class TaskRunningError extends ApiError {
  constructor(detail?: unknown) {
    super('任务仍在执行中', 202, detail);
    this.name = 'TaskRunningError';
  }
}

async function request<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text().catch(() => undefined);
    }
    throw new ApiError(
      `API ${res.status} ${res.statusText}`,
      res.status,
      detail,
    );
  }

  // 202 表示任务仍在执行
  if (res.status === 202) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = undefined;
    }
    throw new TaskRunningError(detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const briefingApi = {
  /** 创建日报任务（POST /api/briefings） */
  async create(query: string): Promise<CreateBriefingResponse> {
    return request<CreateBriefingResponse>('/briefings', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  },

  /** 获取报告详情（GET /api/briefings/{task_id}） */
  async getReport(taskId: string): Promise<ReportDetail> {
    return request<ReportDetail>(`/briefings/${taskId}`);
  },

  /** 获取历史报告列表（GET /api/briefings） */
  async list(
    page = 1,
    pageSize = 20,
    keyword = '',
  ): Promise<BriefingListResponse> {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      keyword,
    });
    return request<BriefingListResponse>(`/briefings?${params.toString()}`);
  },

  /** 下载 Markdown 报告（GET /api/briefings/{task_id}/download） */
  async download(taskId: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/briefings/${taskId}/download`);
    if (!res.ok) {
      throw new ApiError('下载失败', res.status);
    }
    return res.blob();
  },

  /** 健康检查（GET /api/health） */
  async health(): Promise<{ status: string; timestamp: string }> {
    return request('/health');
  },
};
