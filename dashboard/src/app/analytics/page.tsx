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
} from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface DashboardStats {
    intelligence_total: number;
    intelligence_today: number;
    content_total: number;
    content_published: number;
    actions_pending: number;
    actions_completed: number;
    opposition_alerts: number;
}

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function AnalyticsPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const res = await fetch('/api/metrics/dashboard');
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Failed to fetch analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    // Mock data for charts
    const sourceData = [
        { name: 'News', value: 45 },
        { name: 'Twitter', value: 30 },
        { name: 'Legislative', value: 15 },
        { name: 'Reddit', value: 10 },
    ];

    const weeklyData = [
        { day: 'Mon', intelligence: 24, content: 12, actions: 8 },
        { day: 'Tue', intelligence: 35, content: 18, actions: 12 },
        { day: 'Wed', intelligence: 28, content: 15, actions: 10 },
        { day: 'Thu', intelligence: 42, content: 22, actions: 15 },
        { day: 'Fri', intelligence: 38, content: 20, actions: 18 },
        { day: 'Sat', intelligence: 18, content: 8, actions: 5 },
        { day: 'Sun', intelligence: 15, content: 5, actions: 3 },
    ];

    const engagementData = Array.from({ length: 30 }, (_, i) => ({
        day: i + 1,
        engagement: Math.floor(Math.random() * 1000) + 200,
    }));

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Analytics</h1>
                    <p className="text-[var(--muted)] mt-2">
                        Campaign performance and system metrics
                    </p>
                </header>

                {/* Key Metrics */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <MetricCard
                        title="Total Intelligence"
                        value={stats?.intelligence_total || 0}
                        change={12}
                        loading={loading}
                    />
                    <MetricCard
                        title="Content Published"
                        value={stats?.content_published || 0}
                        change={8}
                        loading={loading}
                    />
                    <MetricCard
                        title="Actions Completed"
                        value={stats?.actions_completed || 0}
                        change={-3}
                        loading={loading}
                    />
                    <MetricCard
                        title="Opposition Responded"
                        value={Math.floor((stats?.opposition_alerts || 0) * 0.7)}
                        change={25}
                        loading={loading}
                    />
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-3 gap-6 mb-8">
                    {/* Weekly Activity */}
                    <div className="col-span-2 bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4">Weekly Activity</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={weeklyData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                                <XAxis dataKey="day" stroke="#64748b" />
                                <YAxis stroke="#64748b" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#12121a',
                                        border: '1px solid #2a2a3a',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Bar dataKey="intelligence" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="content" fill="#22c55e" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="actions" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Source Distribution */}
                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4">Intelligence Sources</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={sourceData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {sourceData.map((_, index) => (
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
                            {sourceData.map((entry, i) => (
                                <div key={entry.name} className="flex items-center gap-2">
                                    <div
                                        className="w-3 h-3 rounded-full"
                                        style={{ backgroundColor: COLORS[i] }}
                                    />
                                    <span className="text-sm text-[var(--muted)]">{entry.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Engagement Trend */}
                <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Engagement Trend (30 days)</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={engagementData}>
                            <defs>
                                <linearGradient id="colorEngagement" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                            <XAxis dataKey="day" stroke="#64748b" />
                            <YAxis stroke="#64748b" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#12121a',
                                    border: '1px solid #2a2a3a',
                                    borderRadius: '8px',
                                }}
                            />
                            <Area
                                type="monotone"
                                dataKey="engagement"
                                stroke="#8b5cf6"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorEngagement)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </main>
        </div>
    );
}

function MetricCard({
    title,
    value,
    change,
    loading,
}: {
    title: string;
    value: number;
    change: number;
    loading: boolean;
}) {
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
            <div className={`flex items-center gap-1 mt-2 ${trendColor}`}>
                <TrendIcon className="w-4 h-4" />
                <span className="text-sm font-medium">{Math.abs(change)}%</span>
                <span className="text-xs text-[var(--muted)]">vs last week</span>
            </div>
        </div>
    );
}
