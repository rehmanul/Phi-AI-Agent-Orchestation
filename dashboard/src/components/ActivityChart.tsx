'use client';

import { useState, useEffect } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';

interface ActivityData {
    timestamp: string;
    value: number;
}

export default function ActivityChart() {
    const [data, setData] = useState<ActivityData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const res = await fetch('/api/metrics/timeline?metric_type=distribution&hours=24&interval_minutes=60');
            if (res.ok) {
                const result = await res.json();
                setData(result.data || generateMockData());
            } else {
                setData(generateMockData());
            }
        } catch (error) {
            setData(generateMockData());
        } finally {
            setLoading(false);
        }
    };

    const generateMockData = (): ActivityData[] => {
        const now = new Date();
        return Array.from({ length: 24 }, (_, i) => {
            const timestamp = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
            return {
                timestamp: timestamp.toISOString(),
                value: Math.floor(Math.random() * 50) + 10,
            };
        });
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true });
    };

    return (
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-semibold">Activity Overview</h3>
                    <p className="text-sm text-[var(--muted)]">Last 24 hours</p>
                </div>
                <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                        <span className="text-[var(--muted)]">Activity</span>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="h-64 bg-[var(--card-hover)] rounded-lg animate-pulse" />
            ) : (
                <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={formatTime}
                            stroke="#64748b"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis
                            stroke="#64748b"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `${value}`}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#12121a',
                                border: '1px solid #2a2a3a',
                                borderRadius: '8px',
                                color: '#f8fafc',
                            }}
                            labelFormatter={(value) => new Date(value).toLocaleString()}
                            formatter={(value: number) => [value, 'Actions']}
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
    );
}
