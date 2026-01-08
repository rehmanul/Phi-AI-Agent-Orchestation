'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    AreaChart,
    Area,
    LineChart,
    Line,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';

interface DashboardStats {
    intelligence_total: number;
    intelligence_today: number;
    content_total: number;
    content_published: number;
    actions_pending: number;
    actions_completed: number;
    opposition_alerts: number;
}

interface TimelineData {
    timestamp: string;
    value: number;
}

interface SourceStats {
    by_source: Record<string, number>;
    total: number;
}

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function AnalyticsPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [sourceStats, setSourceStats] = useState<SourceStats | null>(null);
    const [activityData, setActivityData] = useState<TimelineData[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        fetchAllData();
    }, []);

    const fetchAllData = async () => {
        setLoading(true);
        await Promise.all([
            fetchStats(),
            fetchSourceStats(),
            fetchActivityTimeline(),
        ]);
        setLoading(false);
    };

    const refreshData = async () => {
        setRefreshing(true);
        await fetchAllData();
        setRefreshing(false);
    };

    const fetchStats = async () => {
        try {
            const res = await fetch('/api/metrics/dashboard');
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        }
    };

    const fetchSourceStats = async () => {
        try {
            const res = await fetch('/api/intelligence/stats/summary');
            if (res.ok) {
                const data = await res.json();
                setSourceStats(data);
            }
        } catch (error) {
            console.error('Failed to fetch source stats:', error);
        }
    };

    const fetchActivityTimeline = async () => {
        try {
            const res = await fetch('/api/metrics/timeline?metric_type=distribution&hours=168&interval_minutes=60');
            if (res.ok) {
                const data = await res.json();
                setActivityData(data.data || []);
            }
        } catch (error) {
            console.error('Failed to fetch timeline:', error);
        }
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };

    // Transform source stats for pie chart
    const pieData = sourceStats?.by_source
        ? Object.entries(sourceStats.by_source).map(([name, value]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            value,
        }))
        : [];

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold">Analytics</h1>
                        <p className="text-[var(--muted)] mt-2">
                            Campaign performance and system metrics
                        </p>
                    </div>
                    <button
                        onClick={refreshData}
                        disabled={refreshing}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-white hover:bg-[var(--card-hover)]"
                    >
                        <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </header>

                {/* Key Metrics */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <MetricCard
                        title="Total Intelligence"
                        value={stats?.intelligence_total || 0}
                        previousValue={0}
                        loading={loading}
                    />
                    <MetricCard
                        title="Content Published"
                        value={stats?.content_published || 0}
                        previousValue={0}
                        loading={loading}
                    />
                    <MetricCard
                        title="Actions Completed"
                        value={stats?.actions_completed || 0}
                        previousValue={0}
                        loading={loading}
                    />
                    <MetricCard
                        title="Opposition Alerts"
                        value={stats?.opposition_alerts || 0}
                        previousValue={0}
                        loading={loading}
                    />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-3 gap-6 mb-8">
                    {/* Activity Timeline */}
                    <div className="col-span-2 bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4">Activity Timeline (7 days)</h3>
                        {loading ? (
                            <div className="h-64 bg-[var(--card-hover)] rounded-lg animate-pulse" />
                        ) : activityData.length === 0 ? (
                            <div className="h-64 flex items-center justify-center text-[var(--muted)]">
                                No activity data available yet
                            </div>
                        ) : (
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={activityData}>
                                    <defs>
                                        <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                                    <XAxis dataKey="timestamp" tickFormatter={formatTime} stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#12121a',
                                            border: '1px solid #2a2a3a',
                                            borderRadius: '8px',
                                        }}
                                        labelFormatter={(value) => new Date(value).toLocaleString()}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="value"
                                        stroke="#3b82f6"
                                        strokeWidth={2}
                                        fillOpacity={1}
                                        fill="url(#colorActivity)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        )}
                    </div>

                    {/* Source Distribution */}
                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4">Intelligence by Source</h3>
                        {loading ? (
                            <div className="h-64 bg-[var(--card-hover)] rounded-lg animate-pulse" />
                        ) : pieData.length === 0 ? (
                            <div className="h-64 flex items-center justify-center text-[var(--muted)]">
                                No source data available
                            </div>
                        ) : (
                            <>
                                <ResponsiveContainer width="100%" height={200}>
                                    <PieChart>
                                        <Pie
                                            data={pieData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={50}
                                            outerRadius={80}
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {pieData.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#12121a',
                                                border: '1px solid #2a2a3a',
                                                borderRadius: '8px',
                                            }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="flex flex-wrap gap-4 justify-center mt-4">
                                    {pieData.map((entry, i) => (
                                        <div key={entry.name} className="flex items-center gap-2">
                                            <div
                                                className="w-3 h-3 rounded-full"
                                                style={{ backgroundColor: COLORS[i % COLORS.length] }}
                                            />
                                            <span className="text-sm text-[var(--muted)]">
                                                {entry.name} ({entry.value})
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Stats Summary */}
                <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">System Summary</h3>
                    <div className="grid grid-cols-4 gap-6">
                        <div className="text-center">
                            <p className="text-3xl font-bold">{stats?.intelligence_today || 0}</p>
                            <p className="text-sm text-[var(--muted)]">Intelligence Today</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-bold">{stats?.content_total || 0}</p>
                            <p className="text-sm text-[var(--muted)]">Total Content</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-bold">{stats?.actions_pending || 0}</p>
                            <p className="text-sm text-[var(--muted)]">Actions Pending</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-bold">{sourceStats?.total || 0}</p>
                            <p className="text-sm text-[var(--muted)]">Total Sources Scanned</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

function MetricCard({
    title,
    value,
    previousValue,
    loading,
}: {
    title: string;
    value: number;
    previousValue: number;
    loading: boolean;
}) {
    const change = previousValue > 0 ? ((value - previousValue) / previousValue) * 100 : 0;
    const TrendIcon = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Minus;
    const trendColor = change > 0 ? 'text-green-400' : change < 0 ? 'text-red-400' : 'text-gray-400';

    return (
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
            <p className="text-sm text-[var(--muted)] font-medium">{title}</p>
            {loading ? (
                <div className="h-9 w-20 bg-[var(--border)] rounded animate-pulse mt-2" />
            ) : (
                <p className="text-3xl font-bold mt-2">{value.toLocaleString()}</p>
            )}
            {previousValue > 0 && (
                <div className={`flex items-center gap-1 mt-2 ${trendColor}`}>
                    <TrendIcon className="w-4 h-4" />
                    <span className="text-sm font-medium">{Math.abs(change).toFixed(1)}%</span>
                </div>
            )}
        </div>
    );
}
