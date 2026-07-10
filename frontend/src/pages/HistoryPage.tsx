// 历史报告列表页面

import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, History, FileText, ChevronRight } from 'lucide-react';
import { briefingApi, ApiError } from '@/services/briefingApi';
import type { BriefingListItem } from '@/types/briefing';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { EmptyState } from '@/components/common/EmptyState';
import { FullScreenLoader } from '@/components/common/LoadingSpinner';
import { cn } from '@/lib/utils';

const PAGE_SIZE = 20;

function formatDateTime(iso?: string): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

const statusConfig = {
  running: { tone: 'accent' as const, label: '执行中' },
  success: { tone: 'success' as const, label: '已完成' },
  failed: { tone: 'danger' as const, label: '失败' },
};

export function HistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<BriefingListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchList = useCallback(async (p: number, kw: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await briefingApi.list(p, PAGE_SIZE, kw);
      setItems(res.items);
      setTotal(res.total);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? `加载失败：${err.message}`
          : err instanceof Error
            ? err.message
            : '未知错误';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchList(1, '');
  }, [fetchList]);

  const handleSearch = () => {
    setPage(1);
    fetchList(1, keyword);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    fetchList(newPage, keyword);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="animate-fade-in">
      {/* 页面标题 */}
      <div className="flex items-center gap-2 mb-6">
        <History className="w-5 h-5 text-accent-light" />
        <h1 className="text-xl font-semibold text-gray-100">历史报告</h1>
        {total > 0 && (
          <span className="text-sm text-gray-500">共 {total} 条</span>
        )}
      </div>

      {/* 搜索栏 */}
      <div className="flex gap-2 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="搜索项目名称或商品..."
            className="w-full glass rounded-lg pl-9 pr-3 py-2 text-sm text-gray-200 placeholder:text-gray-500 outline-none focus:border-accent/40"
          />
        </div>
        <Button onClick={handleSearch} variant="secondary" size="md">
          搜索
        </Button>
      </div>

      {/* 内容区 */}
      {loading ? (
        <FullScreenLoader label="加载历史报告..." />
      ) : error ? (
        <Card padding="lg" className="text-center">
          <EmptyState
            title="加载失败"
            description={error}
            action={
              <Button onClick={() => fetchList(1, '')} variant="secondary">
                重试
              </Button>
            }
          />
        </Card>
      ) : items.length === 0 ? (
        <Card padding="lg">
          <EmptyState
            icon={<FileText className="w-10 h-10" />}
            title={keyword ? '未找到匹配的报告' : '暂无历史报告'}
            description={
              keyword
                ? '尝试更换搜索关键词'
                : '在首页输入查询，生成你的第一份日报'
            }
            action={
              !keyword && (
                <Button onClick={() => navigate('/')} size="sm">
                  去创建日报
                </Button>
              )
            }
          />
        </Card>
      ) : (
        <>
          <div className="space-y-2">
            {items.map((item) => {
              const config = statusConfig[item.status] ?? statusConfig.success;
              const targetPath =
                item.status === 'running'
                  ? `/briefings/${item.task_id}`
                  : `/briefings/${item.task_id}/detail`;
              return (
                <Card
                  key={item.task_id}
                  hoverable
                  padding="md"
                  onClick={() => navigate(targetPath)}
                  className="group"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-start gap-3 min-w-0 flex-1">
                      <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-accent-light" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors truncate">
                            {item.title}
                          </h3>
                          <Badge tone={config.tone} dot={item.status === 'running'}>
                            {config.label}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          {item.project && <span>{item.project}</span>}
                          {item.commodity && (
                            <span className="text-accent-light/60">
                              {item.commodity}
                            </span>
                          )}
                          <span>{formatDateTime(item.created_at)}</span>
                          {item.warning_count > 0 && (
                            <span className="text-amber-400/70">
                              {item.warning_count} 条警告
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-accent-light group-hover:translate-x-0.5 transition-all flex-shrink-0" />
                  </div>
                </Card>
              );
            })}
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
                variant="ghost"
                size="sm"
              >
                上一页
              </Button>
              <span className="text-sm text-gray-400 px-3">
                {page} / {totalPages}
              </span>
              <Button
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
                variant="ghost"
                size="sm"
              >
                下一页
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
