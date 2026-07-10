// 矿权日报 Agent 前端类型定义
// 与后端 serve/app.py 的 API 响应结构保持一致

/** 任务状态 */
export type TaskStatus = 'running' | 'success' | 'failed';

/** 前端综合状态（包含 idle / creating） */
export type BriefingStatus = TaskStatus | 'idle' | 'creating';

/** 节点事件类型（与后端 SSE 事件一致） */
export type NodeEventType =
  | 'node_start'
  | 'node_warning'
  | 'node_success'
  | 'task_done'
  | 'task_failed';

/** LangGraph 节点名称 */
export type NodeName =
  | 'parse_intent'
  | 'resolve_asset'
  | 'search_news'
  | 'expand_news_days'
  | 'fetch_articles'
  | 'extract_resources'
  | 'fetch_price'
  | 'analyze_context'
  | 'generate_risks'
  | 'render_report'
  | 'quality_check'
  | 'revise_report'
  | 'save_report'
  | 'save_report_with_warnings';

/** SSE 推送的节点事件 */
export interface NodeEvent {
  type: NodeEventType;
  node?: NodeName;
  message: string;
  payload?: Record<string, unknown>;
  timestamp: string;
  task_id?: string;
  report_url?: string;
}

/** 前端维护的节点执行状态 */
export type NodeRunStatus =
  | 'pending'
  | 'running'
  | 'success'
  | 'warning'
  | 'skipped';

/** 节点运行时信息（前端维护） */
export interface NodeRunInfo {
  name: NodeName;
  label: string;
  status: NodeRunStatus;
  message?: string;
  payload?: Record<string, unknown>;
  startedAt?: string;
  finishedAt?: string;
}

/** 创建日报请求 */
export interface CreateBriefingRequest {
  query: string;
}

/** 创建日报响应 */
export interface CreateBriefingResponse {
  task_id: string;
  status: string;
}

/** 新闻条目（来自 search_news 节点） */
export interface NewsItem {
  title: string;
  url?: string;
  published?: string;
  published_at?: string;
  source?: string;
  summary?: string;
  content?: string;
  citations?: string[];
  warning?: string;
}

/** 文章（带正文，来自 fetch_articles 节点） */
export type Article = NewsItem;

/** 带单位的量值 */
export interface Quantity {
  value: number;
  unit: string;
}

/** 资源量条目（与 mineral_pdf_mcp 的 Mock 数据结构一致） */
export interface ResourceItem {
  category: string;
  ore_tonnage?: Quantity;
  grade?: Quantity;
  contained_metal?: Quantity;
  page?: number;
  confidence?: number;
  source?: string;
}

/** 资源量数据集合 */
export interface ResourceData {
  resources: ResourceItem[];
  report_url?: string;
  source?: string;
}

/** 价格信息（sections.price）
 *
 * 注意：后端 observations 是字符串数组（文字描述），
 * 不是 {date, price} 数组。
 */
export interface PriceInfo {
  commodity: string;
  latest_price: number;
  unit: string;
  change_pct: number;
  ma_7: number;
  ma_30: number;
  trend: 'up' | 'down' | 'flat';
  observations: string[];
}

/** 风险条目（后端返回字符串数组，前端兼容字符串和对象两种格式） */
export type RiskItem = string | {
  title: string;
  level?: 'high' | 'medium' | 'low';
  description: string;
  mitigation?: string;
};

/** 引用源类型 */
export type CitationType = 'news' | 'pdf' | 'price' | 'other';

/** 引用源 */
export interface Citation {
  title: string;
  url: string;
  type: CitationType;
}

/** 报告摘要 */
export interface ReportSummary {
  news_count: number;
  resource_available: boolean;
  price_available: boolean;
  warning_count: number;
}

/** 报告章节 */
export interface ReportSections {
  news: NewsItem[];
  resources: ResourceItem[];
  price: PriceInfo;
  risks: RiskItem[];
}

/** 报告详情响应（GET /api/briefings/{task_id}） */
export interface ReportDetail {
  task_id: string;
  title: string;
  project: string;
  commodity: string;
  status: TaskStatus;
  created_at: string;
  finished_at: string | null;
  markdown: string;
  summary: ReportSummary;
  sections: ReportSections;
  citations: Citation[];
  warnings: string[];
}

/** 历史报告列表项 */
export interface BriefingListItem {
  task_id: string;
  title: string;
  project: string;
  commodity: string;
  status: TaskStatus;
  created_at: string;
  warning_count: number;
}

/** 历史报告列表响应（GET /api/briefings） */
export interface BriefingListResponse {
  items: BriefingListItem[];
  total: number;
}
