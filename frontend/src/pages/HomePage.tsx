// 首页：输入查询、触发日报任务

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, GitBranch, ShieldCheck } from 'lucide-react';
import { PromptInput } from '@/components/briefing/PromptInput';
import { useCreateBriefing } from '@/hooks/useCreateBriefing';
import { useBriefingStore } from '@/store/briefingStore';

const FEATURES = [
  {
    icon: Bot,
    title: '多源数据采集',
    desc: '通过 3 个 MCP Server 获取矿业新闻、资源量 PDF、LME 价格数据',
  },
  {
    icon: GitBranch,
    title: 'LangGraph 可视化',
    desc: '14 节点工作流实时展示执行进度，支持质检循环与降级兜底',
  },
  {
    icon: ShieldCheck,
    title: '风险智能识别',
    desc: '通义千问增强风险生成与质检，确保日报质量与可信引用',
  },
];

export function HomePage() {
  const navigate = useNavigate();
  const { create, loading, error } = useCreateBriefing();
  const reset = useBriefingStore((s) => s.reset);

  // 进入首页时重置 store（清除上一次任务状态）
  useEffect(() => {
    reset();
  }, [reset]);

  const handleSubmit = async (query: string) => {
    const taskId = await create(query);
    if (taskId) {
      navigate(`/briefings/${taskId}`);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <section className="text-center py-12 md:py-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass text-xs text-gray-400 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-accent animate-breathe" />
          LangGraph + MCP + 通义千问
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-100 mb-4 leading-tight">
          矿权日报
          <span className="bg-gradient-to-r from-accent-light to-accent bg-clip-text text-transparent">
            {' '}智能体
          </span>
        </h1>
        <p className="text-gray-400 text-base max-w-2xl mx-auto mb-10">
          输入矿业项目或商品名称，自动采集新闻、资源量、价格数据，
          <br className="hidden md:block" />
          生成结构化日报与风险提示
        </p>

        <div className="max-w-2xl mx-auto">
          <PromptInput onSubmit={handleSubmit} loading={loading} error={error} />
        </div>
      </section>

      {/* 特性介绍 */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        {FEATURES.map((f) => {
          const Icon = f.icon;
          return (
            <div key={f.title} className="glass rounded-xl p-5">
              <div className="w-10 h-10 rounded-lg bg-accent/15 flex items-center justify-center mb-3">
                <Icon className="w-5 h-5 text-accent-light" />
              </div>
              <h3 className="text-sm font-semibold text-gray-100 mb-1.5">
                {f.title}
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          );
        })}
      </section>
    </div>
  );
}
