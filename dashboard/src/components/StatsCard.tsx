'use client';

import { clsx } from 'clsx';

interface StatsCardProps {
    title: string;
    value: number;
    subtitle: string;
    icon: React.ReactNode;
    color: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
    loading?: boolean;
}

const colorClasses = {
    blue: {
        bg: 'bg-blue-500/10',
        text: 'text-blue-400',
        border: 'border-blue-500/20',
        glow: 'shadow-blue-500/10',
    },
    green: {
        bg: 'bg-green-500/10',
        text: 'text-green-400',
        border: 'border-green-500/20',
        glow: 'shadow-green-500/10',
    },
    yellow: {
        bg: 'bg-yellow-500/10',
        text: 'text-yellow-400',
        border: 'border-yellow-500/20',
        glow: 'shadow-yellow-500/10',
    },
    red: {
        bg: 'bg-red-500/10',
        text: 'text-red-400',
        border: 'border-red-500/20',
        glow: 'shadow-red-500/10',
    },
    purple: {
        bg: 'bg-purple-500/10',
        text: 'text-purple-400',
        border: 'border-purple-500/20',
        glow: 'shadow-purple-500/10',
    },
};

export default function StatsCard({
    title,
    value,
    subtitle,
    icon,
    color,
    loading,
}: StatsCardProps) {
    const colors = colorClasses[color];

    return (
        <div
            className={clsx(
                'p-6 rounded-xl border transition-all duration-300 hover:scale-105',
                'bg-[var(--card)] border-[var(--border)]',
                `hover:${colors.border} hover:shadow-lg hover:${colors.glow}`
            )}
        >
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-[var(--muted)] font-medium">{title}</p>
                    {loading ? (
                        <div className="h-9 w-20 bg-[var(--border)] rounded animate-pulse mt-2" />
                    ) : (
                        <p className="text-3xl font-bold mt-2">{value.toLocaleString()}</p>
                    )}
                    <p className={clsx('text-sm mt-2', colors.text)}>{subtitle}</p>
                </div>
                <div className={clsx('p-3 rounded-lg', colors.bg, colors.text)}>
                    {icon}
                </div>
            </div>
        </div>
    );
}
