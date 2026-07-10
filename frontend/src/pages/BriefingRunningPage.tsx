// 日报执行中页面：展示 LangGraph 节点进度与运行日志

import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft, FileText } from 'lucide-react';
import { useBriefingStore } from '@/store/briefingStore';
import { useBriefingEvents } from '@/hooks/useBriefingEvents';
import { useBriefingReport } from '@/hooks/useBriefingReport';
import { GraphProgress } from '@/components/briefing/GraphProgress';
import { RuntimeLogPanel } from '@/components/briefing/RuntimeLogPanel';
import { Card, CardHeader } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';
import { DotLoader } from '@/components/common/LoadingSpinner';

export function BriefingRunningPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  const storeTaskId = useBriefingStore((s) => s.taskId);
  const query = useBriefingStore((s) => s.query);
  const status = useBriefingStore((s) => s.status);
  const error = useBriefingStore((s) => s.error);
  const startTask = useBriefingStore((s) => s.startTask);
  const events = useBriefingStore((s) => s.events);

  // 刷新场景：若 store.taskId 与 URL 不匹配，重置并让 SSE 重放事件
  useEffect(() => {
    if (taskId && storeTaskId !== taskId) {
      startTask(taskId, '');
    }
  }, [taskId, storeTaskId, startTask]);

  // 订阅 SSE 事件
  useBriefingEvents({
    taskId: taskId ?? null,
    enabled: !!taskId,
    onDone: () => {
      if (taskId) {
        navigate(`/briefings/${taskId}/detail`, { replace: true });
      }
    },
  });

  // 状态变为 success 时也跳转（兜底，防止 onDone 未触发）
  useEffect(() => {
    if (status === 'success' && taskId) {
      navigate(`/briefings/${taskId}/detail`, { replace: true });
    }
  }, [status, taskId, navigate]);

  if (!taskId) {
    navigate('/');
    return null;
  }

  // 错误状态
  if (status === 'failed') {
    return (
      <div className="animate-fade-in">
        <Card padding="lg" className="max-w-xl mx-auto mt-12 text-center">
          <div className="w-12 h-12 rounded-full bg-red-500/15 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-100 mb-2">
            任务执行失败
          </h2>
          <p className="text-sm text-gray-400 mb-6">
            {error || '未知错误'}
          </p>
          <Button onClick={() => navigate('/')} variant="secondary">
            返回首页
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* 顶部信息栏 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={() => navigate('/')}
            className="p-1.5 rounded-md text-gray-400 hover:text-gray-200 hover:bg-white/5 transition-colors"
            aria-label="返回首页"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-base font-semibold text-gray-100 truncate">
                {query || '正在执行日报任务'}
              </h1>
              <Badge tone="accent" dot>
                执行中
              </Badge>
            </div>
            <p className="text-xs text-gray-500 mt-0.5 font-mono">
              {taskId}
            </p>
          </div>
        </div>
        <DotLoader className="text-accent" />
      </div>

      {/* 主体：左侧节点流程 + 右侧运行日志 */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-2">
          <Card padding="md" className="h-full">
            <CardHeader
              title="执行流程"
              subtitle="LangGraph 节点状态"
              icon={<FileText className="w-4 h-4" />}
            />
            <GraphProgress />
          </Card>
        </div>
        <div className="lg:col-span-3">
          <RuntimeLogPanel />
        </div>
      </div>

      {/* 底部事件计数 */}
      {events.length > 0 && (
        <div className="mt-4 text-center text-xs text-gray-600">
          已接收 {events.length} 个事件
        </div>
      )}
    </div>
  );
}
