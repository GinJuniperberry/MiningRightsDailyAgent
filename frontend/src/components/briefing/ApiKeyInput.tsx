// API Key 配置输入框
// 首页配置通义千问 API Key，持久化到 localStorage

import { useState } from 'react';
import { Key, Eye, EyeOff, CheckCircle2, Info } from 'lucide-react';
import { useBriefingStore } from '@/store/briefingStore';
import { Badge } from '@/components/common/Badge';
import { cn } from '@/lib/utils';

export function ApiKeyInput() {
  const apiKey = useBriefingStore((s) => s.apiKey);
  const setApiKey = useBriefingStore((s) => s.setApiKey);
  const [visible, setVisible] = useState(false);
  const [expanded, setExpanded] = useState(!apiKey);

  return (
    <div className="w-full mt-3">
      {/* 折叠状态：只显示一行状态 */}
      {!expanded && (
        <button
          onClick={() => setExpanded(true)}
          className={cn(
            'flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300',
            'transition-colors',
          )}
        >
          <Key className="w-3.5 h-3.5" />
          {apiKey ? (
            <>
              <span>API Key 已配置</span>
              <Badge tone="success" dot>LLM 已启用</Badge>
            </>
          ) : (
            <>
              <span>未配置 API Key，走规则模式</span>
              <Badge tone="muted">点击配置</Badge>
            </>
          )}
        </button>
      )}

      {/* 展开状态：输入框 */}
      {expanded && (
        <div className="glass rounded-xl p-3 animate-fade-in">
          <div className="flex items-center gap-2 mb-2">
            <Key className="w-3.5 h-3.5 text-accent-light" />
            <span className="text-xs font-medium text-gray-300">通义千问 API Key</span>
            {apiKey && (
              <Badge tone="success" dot>已启用</Badge>
            )}
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                type={visible ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-...（留空则走纯规则模式）"
                className={cn(
                  'w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 pr-9',
                  'text-sm text-gray-100 placeholder:text-gray-600',
                  'outline-none focus:border-accent/40 transition-colors',
                )}
                autoComplete="off"
                spellCheck={false}
              />
              <button
                onClick={() => setVisible(!visible)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                type="button"
              >
                {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            <button
              onClick={() => setExpanded(false)}
              className={cn(
                'px-3 py-2 rounded-lg text-xs glass glass-hover',
                'text-gray-400 hover:text-gray-200 transition-colors',
              )}
              type="button"
            >
              收起
            </button>
          </div>

          <div className="flex items-start gap-1.5 mt-2 text-xs text-gray-500">
            {apiKey ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-green-400 flex-shrink-0 mt-0.5" />
                <span>已保存到浏览器，生成日报时将使用此 Key 调用通义千问增强摘要与风险生成。</span>
              </>
            ) : (
              <>
                <Info className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                <span>不配置也可使用，Agent 走纯规则模式生成日报。配置后自动启用 LLM 增强。</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
