// 应用入口：路由配置
// /                  → 首页（输入查询）
// /briefings/:taskId → 执行中页面（SSE 实时进度）
// /briefings/:taskId/detail → 报告详情
// /history           → 历史报告列表

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { HomePage } from '@/pages/HomePage';
import { BriefingRunningPage } from '@/pages/BriefingRunningPage';
import { BriefingDetailPage } from '@/pages/BriefingDetailPage';
import { HistoryPage } from '@/pages/HistoryPage';

export default function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/briefings/:taskId" element={<BriefingRunningPage />} />
          <Route
            path="/briefings/:taskId/detail"
            element={<BriefingDetailPage />}
          />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}
