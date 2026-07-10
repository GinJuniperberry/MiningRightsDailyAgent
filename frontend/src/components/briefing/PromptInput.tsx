// 日报查询输入框
// 首页核心交互：输入查询、提交任务、提供示例

import { useState, type KeyboardEvent } from 'react';
import { ArrowRight, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { cn } from '@/lib/utils';

const EXAMPLE_QUERIES = [
  '给我生成一份关于 Pilbara 锂矿的今日简报',
  'Greenbushes 锂矿最新动态和资源量分析',
  'Mount Cattlin 今日行情与风险提示',
];

export interface PromptInputProps {
  onSubmit: (query: string) => void;
  loading?: boolean;
  error?: string | null;
}

export function PromptInput({ onSubmit, loading = false, error }: PromptInputProps) {
  const [value, setValue] = useState('');

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Cmd/Ctrl + Enter 提交
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="w-full">
      <div
        className={cn(
          'glass rounded-2xl p-1.5 transition-all duration-200',
          'focus-within:border-accent/40 focus-within:shadow-lg focus-within:shadow-accent/10',
        )}
      >
        <div className="flex items-end gap-2">
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="描述你想了解的矿业项目、商品或风险话题..."
            rows={3}
            className={cn(
              'flex-1 bg-transparent px-4 py-3 text-sm text-gray-100',
              'placeholder:text-gray-500 resize-none outline-none',
              'font-sans',
            )}
            disabled={loading}
          />
          <Button
            onClick={submit}
            loading={loading}
            disabled={!value.trim()}
            size="lg"
            className="mb-1.5 mr-1.5"
            rightIcon={!loading && <ArrowRight className="w-4 h-4" />}
          >
            生成日报
          </Button>
        </div>
      </div>

      {error && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-300 animate-fade-in">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="mt-5">
        <div className="flex items-center gap-1.5 mb-2.5 text-xs text-gray-500">
          <Sparkles className="w-3.5 h-3.5" />
          <span>试试这些示例</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => !loading && setValue(q)}
              disabled={loading}
              className={cn(
                'px-3 py-1.5 rounded-lg text-xs text-left transition-all',
                'glass glass-hover text-gray-400 hover:text-gray-200',
                'disabled:opacity-50 disabled:cursor-not-allowed',
              )}
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
