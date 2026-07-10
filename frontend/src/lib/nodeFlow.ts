// LangGraph 节点流程定义
// 与后端 agent/graph.py 和 serve/app.py 的 NODE_LABELS 保持一致

import type { NodeName } from '@/types/briefing';

/** 节点显示标签映射 */
export const NODE_LABELS: Record<string, string> = {
  parse_intent: '解析用户输入',
  resolve_asset: '识别矿权信息',
  search_news: '搜索矿业新闻',
  expand_news_days: '扩大搜索范围',
  fetch_articles: '抓取新闻正文',
  extract_resources: '抽取资源量数据',
  fetch_price: '获取价格行情',
  analyze_context: '聚合上下文',
  generate_risks: '生成风险提示',
  render_report: '渲染日报',
  quality_check: '质量检查',
  revise_report: '修订报告',
  save_report: '保存报告',
  save_report_with_warnings: '保存报告（带警告）',
};

/** 节点流程顺序（主流程展示用）
 *
 * 说明：
 * - expand_news_days 是 search_news 的条件分支，不在主流程展示
 * - revise_report 是 quality_check 的条件分支，仅在质检失败时出现
 * - save_report 与 save_report_with_warnings 互斥（质检通过 vs 达到修订上限）
 */
export const NODE_FLOW: { name: NodeName; label: string }[] = [
  { name: 'parse_intent', label: NODE_LABELS.parse_intent },
  { name: 'resolve_asset', label: NODE_LABELS.resolve_asset },
  { name: 'search_news', label: NODE_LABELS.search_news },
  { name: 'fetch_articles', label: NODE_LABELS.fetch_articles },
  { name: 'extract_resources', label: NODE_LABELS.extract_resources },
  { name: 'fetch_price', label: NODE_LABELS.fetch_price },
  { name: 'analyze_context', label: NODE_LABELS.analyze_context },
  { name: 'generate_risks', label: NODE_LABELS.generate_risks },
  { name: 'render_report', label: NODE_LABELS.render_report },
  { name: 'quality_check', label: NODE_LABELS.quality_check },
  { name: 'revise_report', label: NODE_LABELS.revise_report },
  { name: 'save_report', label: NODE_LABELS.save_report },
  { name: 'save_report_with_warnings', label: NODE_LABELS.save_report_with_warnings },
];

/** 获取节点显示标签 */
export function getNodeLabel(name: string): string {
  return NODE_LABELS[name] ?? name;
}

/** 判断节点是否属于"结束类"节点（保存报告） */
export function isSaveNode(name: string): boolean {
  return name === 'save_report' || name === 'save_report_with_warnings';
}

/** 判断节点是否为条件分支节点（可能不执行） */
export function isConditionalNode(name: string): boolean {
  return (
    name === 'expand_news_days' ||
    name === 'revise_report' ||
    name === 'save_report_with_warnings'
  );
}
