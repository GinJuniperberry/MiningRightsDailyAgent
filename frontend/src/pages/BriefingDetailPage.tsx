// 日报详情页面：展示完整报告与结构化数据

import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft,
  Download,
  Calendar,
  Flag,
  AlertCircle,
} from 'lucide-react';
import { useBriefingReport } from '@/hooks/useBriefingReport';
import { useDownloadReport } from '@/hooks/useDownloadReport';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { Card } from '@/components/common/Card';
import { FullScreenLoader } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { SummaryCards } from '@/components/briefing/SummaryCards';
import { WarningsPanel } from '@/components/briefing/WarningsPanel';
import { MarkdownReport } from '@/components/briefing/MarkdownReport';
import { NewsList } from '@/components/briefing/NewsList';
import { ResourceTable } from '@/components/briefing/ResourceTable';
import { PriceTrendChart } from '@/components/briefing/PriceTrendChart';
import { RiskList } from '@/components/briefing/RiskList';
import { CitationList } from '@/components/briefing/CitationList';

function formatDateTime(iso?: string | null): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

export function BriefingDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const { report, loading, error } = useBriefingReport(taskId ?? null);
  const { download, loading: downloading } = useDownloadReport();

  // 若任务仍在执行（202），跳转到执行中页面
  useEffect(() => {
    if (!taskId) {
      navigate('/');
    }
  }, [taskId, navigate]);

  if (!taskId) return null;

  if (loading) {
    return <FullScreenLoader label="正在加载报告..." />;
  }

  if (error && !report) {
    return (
      <div className="animate-fade-in">
        <Card padding="lg" className="max-w-xl mx-auto mt-12 text-center">
          <div className="w-12 h-12 rounded-full bg-red-500/15 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-100 mb-2">
            加载报告失败
          </h2>
          <p className="text-sm text-gray-400 mb-6">{error}</p>
          <div className="flex gap-2 justify-center">
            <Button onClick={() => navigate('/')} variant="secondary">
              返回首页
            </Button>
            <Button onClick={() => navigate(`/briefings/${taskId}`)}>
              查看执行过程
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!report) {
    // 任务仍在执行（202），跳转到执行中页面
    return (
      <Card padding="lg" className="max-w-xl mx-auto mt-12 text-center">
        <EmptyState
          title="任务仍在执行中"
          description="即将跳转到执行过程页面"
          action={
            <Button onClick={() => navigate(`/briefings/${taskId}`)}>
              查看执行过程
            </Button>
          }
        />
      </Card>
    );
  }

  const sections = report.sections;

  return (
    <div className="animate-fade-in space-y-4">
      {/* 顶部操作栏 */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={() => navigate('/')}
            className="p-1.5 rounded-md text-gray-400 hover:text-gray-200 hover:bg-white/5 transition-colors"
            aria-label="返回首页"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-lg font-semibold text-gray-100 truncate">
                {report.title}
              </h1>
              <Badge tone="success" dot>
                已完成
              </Badge>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
              {report.project && <span>{report.project}</span>}
              {report.commodity && (
                <span className="text-accent-light/70">
                  {report.commodity}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formatDateTime(report.created_at)}
              </span>
            </div>
          </div>
        </div>
        <Button
          onClick={() => download(taskId)}
          loading={downloading}
          variant="secondary"
          size="sm"
          leftIcon={<Download className="w-3.5 h-3.5" />}
        >
          下载 Markdown
        </Button>
      </div>

      {/* 摘要卡片 */}
      <SummaryCards summary={report.summary} />

      {/* 警告面板 */}
      {report.warnings.length > 0 && (
        <WarningsPanel warnings={report.warnings} />
      )}

      {/* Markdown 完整报告 */}
      <MarkdownReport markdown={report.markdown} />

      {/* 结构化数据区 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <NewsList news={sections.news} limit={8} />
        <RiskList risks={sections.risks} />
      </div>

      <ResourceTable
        resources={sections.resources}
        reportUrl={report.citations.find((c) => c.type === 'pdf')?.url}
      />

      {sections.price && sections.price.latest_price > 0 && (
        <PriceTrendChart price={sections.price} />
      )}

      <CitationList citations={report.citations} />

      {/* 底部导航 */}
      <div className="flex items-center justify-between pt-4 pb-2">
        <Button
          onClick={() => navigate('/history')}
          variant="ghost"
          size="sm"
          leftIcon={<Flag className="w-3.5 h-3.5" />}
        >
          查看历史报告
        </Button>
        <Button onClick={() => navigate('/')} variant="ghost" size="sm">
          生成新日报
        </Button>
      </div>
    </div>
  );
}
