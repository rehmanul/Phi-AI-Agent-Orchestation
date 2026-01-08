'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import StatsCard from '@/components/StatsCard';
import AgentStatusPanel from '@/components/AgentStatusPanel';
import IntelligenceFeed from '@/components/IntelligenceFeed';
import ActivityChart from '@/components/ActivityChart';
import QuickActions from '@/components/QuickActions';
import {
    AlertTriangle,
    FileText,
    Users,
    Zap,
    TrendingUp,
    Clock
} from 'lucide-react';

interface DashboardStats {
    intelligence_total: number;
    intelligence_today: number;
    content_total: number;
    content_published: number;
    actions_pending: number;
    actions_completed: number;
    opposition_alerts: number;
}

export default function Dashboard() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchStats = async () => {
        try {
            const res = await fetch('/api/metrics/dashboard');
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                {/* Header */}
                <header className="mb-8">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                        Advocacy Command Center
                    </h1>
                    <p className="text-[var(--muted)] mt-2">
                        Real-time overview of your grassroots lobbying campaign
                    </p>
                </header>

                {/* Stats Grid */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <StatsCard
                        title="Intelligence Items"
                        value={stats?.intelligence_total || 0}
                        subtitle={`+${stats?.intelligence_today || 0} today`}
                        icon={<Zap className="w-5 h-5" />}
                        color="blue"
                        loading={loading}
                    />
                    <StatsCard
                        title="Content Created"
                        value={stats?.content_total || 0}
                        subtitle={`${stats?.content_published || 0} published`}
                        icon={<FileText className="w-5 h-5" />}
                        color="green"
                        loading={loading}
                    />
                    <StatsCard
                        title="Actions Pending"
                        value={stats?.actions_pending || 0}
                        subtitle={`${stats?.actions_completed || 0} completed`}
                        icon={<Clock className="w-5 h-5" />}
                        color="yellow"
                        loading={loading}
                    />
                    <StatsCard
                        title="Opposition Alerts"
                        value={stats?.opposition_alerts || 0}
                        subtitle="Requires response"
                        icon={<AlertTriangle className="w-5 h-5" />}
                        color="red"
                        loading={loading}
                    />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-3 gap-6 mb-8">
                    {/* Agent Status */}
                    <div className="col-span-1">
                        <AgentStatusPanel />
                    </div>

                    {/* Activity Chart */}
                    <div className="col-span-2">
                        <ActivityChart />
                    </div>
                </div>

                {/* Bottom Section */}
                <div className="grid grid-cols-3 gap-6">
                    {/* Intelligence Feed */}
                    <div className="col-span-2">
                        <IntelligenceFeed />
                    </div>

                    {/* Quick Actions */}
                    <div className="col-span-1">
                        <QuickActions />
                    </div>
                </div>
            </main>
        </div>
    );
}
