// 全局应用骨架
// 提供渐变背景光效 + 顶部 Header + 主内容区域

import type { ReactNode } from 'react';
import { Header } from './Header';

export interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-base-900 bg-gradient-glow">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
      <footer className="max-w-6xl mx-auto px-6 py-6 text-center text-xs text-gray-600">
        基于 LangGraph + MCP + 通义千问 · 矿权日报 Agent
      </footer>
    </div>
  );
}
