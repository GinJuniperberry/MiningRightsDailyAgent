// 顶部导航栏
// 显示品牌标识与主导航

import { Link, useLocation } from 'react-router-dom';
import { Pickaxe, History, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', label: '新建日报', icon: Home },
  { to: '/history', label: '历史报告', icon: History },
];

export function Header() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-30 glass border-b border-white/5">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-dark flex items-center justify-center shadow-lg shadow-accent/30 group-hover:shadow-accent/50 transition-shadow">
            <Pickaxe className="w-4 h-4 text-white" />
          </div>
          <div className="flex flex-col leading-none">
            <span className="text-sm font-semibold text-gray-100">
              矿权日报 Agent
            </span>
            <span className="text-[10px] text-gray-500 mt-0.5">
              Mining Rights Daily Agent
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active =
              item.to === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  'inline-flex items-center gap-1.5 px-3 h-8 rounded-md text-sm transition-all',
                  active
                    ? 'bg-accent/15 text-accent-light'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5',
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
