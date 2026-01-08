'use client';

import { useState } from 'react';
import { clsx } from 'clsx';
import {
    Play,
    FileText,
    Send,
    BarChart3,
    Loader2,
    Check,
} from 'lucide-react';

interface QuickAction {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
    endpoint: string;
    method: 'POST' | 'GET';
    color: string;
}

const actions: QuickAction[] = [
    {
        id: 'scan',
        name: 'Trigger Scan',
        description: 'Run monitoring scan now',
        icon: Play,
        endpoint: '/api/agents/monitoring/scan',
        method: 'POST',
        color: 'blue',
    },
    {
        id: 'brief',
        name: 'Generate Brief',
        description: 'Create intelligence brief',
        icon: FileText,
        endpoint: '/api/agents/analysis/brief',
        method: 'POST',
        color: 'purple',
    },
    {
        id: 'content',
        name: 'Create Content',
        description: 'Generate campaign content',
        icon: Send,
        endpoint: '/api/agents/content/generate',
        method: 'POST',
        color: 'green',
    },
    {
        id: 'report',
        name: 'View Report',
        description: 'Performance analytics',
        icon: BarChart3,
        endpoint: '/api/agents/feedback/report',
        method: 'POST',
        color: 'yellow',
    },
];

const colorMap: Record<string, { bg: string; hover: string; text: string }> = {
    blue: { bg: 'bg-blue-500/10', hover: 'hover:bg-blue-500/20', text: 'text-blue-400' },
    purple: { bg: 'bg-purple-500/10', hover: 'hover:bg-purple-500/20', text: 'text-purple-400' },
    green: { bg: 'bg-green-500/10', hover: 'hover:bg-green-500/20', text: 'text-green-400' },
    yellow: { bg: 'bg-yellow-500/10', hover: 'hover:bg-yellow-500/20', text: 'text-yellow-400' },
};

export default function QuickActions() {
    const [executing, setExecuting] = useState<string | null>(null);
    const [completed, setCompleted] = useState<string | null>(null);

    const executeAction = async (action: QuickAction) => {
        setExecuting(action.id);
        setCompleted(null);

        try {
            const res = await fetch(action.endpoint, {
                method: action.method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content_type: 'tweets', params: { topic: 'wireless power' } }),
            });

            if (res.ok) {
                setCompleted(action.id);
                setTimeout(() => setCompleted(null), 2000);
            }
        } catch (error) {
            console.error('Action failed:', error);
        } finally {
            setExecuting(null);
        }
    };

    return (
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">Quick Actions</h3>

            <div className="space-y-3">
                {actions.map((action) => {
                    const colors = colorMap[action.color];
                    const isExecuting = executing === action.id;
                    const isCompleted = completed === action.id;

                    return (
                        <button
                            key={action.id}
                            onClick={() => executeAction(action)}
                            disabled={isExecuting}
                            className={clsx(
                                'w-full flex items-center gap-4 p-4 rounded-lg transition-all',
                                colors.bg,
                                colors.hover,
                                'disabled:opacity-50 disabled:cursor-not-allowed'
                            )}
                        >
                            <div className={clsx('p-2 rounded-lg bg-[var(--card)]', colors.text)}>
                                {isExecuting ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : isCompleted ? (
                                    <Check className="w-5 h-5" />
                                ) : (
                                    <action.icon className="w-5 h-5" />
                                )}
                            </div>
                            <div className="flex-1 text-left">
                                <p className="font-medium text-sm">{action.name}</p>
                                <p className="text-xs text-[var(--muted)]">{action.description}</p>
                            </div>
                        </button>
                    );
                })}
            </div>

            <div className="mt-6 pt-4 border-t border-[var(--border)]">
                <p className="text-xs text-[var(--muted)] text-center">
                    Actions trigger agent workflows via Kafka
                </p>
            </div>
        </div>
    );
}
