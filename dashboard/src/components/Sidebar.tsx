'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
    LayoutDashboard,
    Radio,
    FileSearch,
    Users,
    FileText,
    Send,
    BarChart3,
    Settings,
    Zap,
} from 'lucide-react';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Intelligence', href: '/intelligence', icon: Radio },
    { name: 'Campaigns', href: '/campaigns', icon: Zap },
    { name: 'Legislators', href: '/legislators', icon: Users },
    { name: 'Content', href: '/content', icon: FileText },
    { name: 'Actions', href: '/actions', icon: Send },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-full w-64 bg-[var(--card)] border-r border-[var(--border)] flex flex-col z-50">
            {/* Logo */}
            <div className="p-6 border-b border-[var(--border)]">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
                        <Zap className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h2 className="font-bold text-lg">Advocacy AI</h2>
                        <p className="text-xs text-[var(--muted)]">Orchestration System</p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4">
                <ul className="space-y-2">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <li key={item.name}>
                                <Link
                                    href={item.href}
                                    className={clsx(
                                        'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                                        isActive
                                            ? 'bg-gradient-primary text-white shadow-lg shadow-blue-500/20'
                                            : 'text-[var(--muted)] hover:bg-[var(--card-hover)] hover:text-white'
                                    )}
                                >
                                    <item.icon className="w-5 h-5" />
                                    <span className="font-medium">{item.name}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Status Footer */}
            <div className="p-4 border-t border-[var(--border)]">
                <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-[var(--card-hover)]">
                    <div className="status-dot status-running" />
                    <div>
                        <p className="text-sm font-medium">System Active</p>
                        <p className="text-xs text-[var(--muted)]">7 agents running</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
