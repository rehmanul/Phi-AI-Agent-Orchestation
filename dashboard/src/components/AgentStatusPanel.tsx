'use client';

import { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import {
    Radio,
    Brain,
    Target,
    Crosshair,
    Pencil,
    Send,
    BarChart,
    RefreshCw,
} from 'lucide-react';

interface AgentStatus {
    status: string;
    last_activity: string | null;
}

const agents = [
    { id: 'monitoring', name: 'Monitoring', icon: Radio, description: 'Scanning sources' },
    { id: 'analysis', name: 'Analysis', icon: Brain, description: 'Fact-checking' },
    { id: 'strategy', name: 'Strategy', icon: Target, description: 'Planning' },
    { id: 'tactics', name: 'Tactics', icon: Crosshair, description: 'Actions' },
    { id: 'content', name: 'Content', icon: Pencil, description: 'Creating' },
    { id: 'distribution', name: 'Distribution', icon: Send, description: 'Delivering' },
    { id: 'feedback', name: 'Feedback', icon: BarChart, description: 'Analytics' },
];

export default function AgentStatusPanel() {
    const [statuses, setStatuses] = useState<Record<string, AgentStatus>>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        fetchStatuses();
        const interval = setInterval(fetchStatuses, 10000);
        return () => clearInterval(interval);
    }, []);

    const fetchStatuses = async () => {
        try {
            const res = await fetch('/api/agents/status');
            if (res.ok) {
                const data = await res.json();
                setStatuses(data);
                setError(false);
            } else {
                setError(true);
            }
        } catch (err) {
            setError(true);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'running':
                return 'status-running';
            case 'paused':
                return 'status-warning';
            case 'error':
                return 'status-error';
            default:
                return 'bg-gray-500';
        }
    };

    return (
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Agent Status</h3>
                <button
                    onClick={fetchStatuses}
                    className="p-2 rounded-lg bg-[var(--card-hover)] hover:bg-[var(--border)] transition-colors"
                >
                    <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin')} />
                </button>
            </div>

            {error && (
                <p className="text-xs text-yellow-400 mb-4">
                    Unable to connect to agent status API
                </p>
            )}

            <div className="space-y-3">
                {agents.map((agent) => {
                    const agentStatus = statuses[agent.id];
                    const status = agentStatus?.status || 'unknown';
                    return (
                        <div
                            key={agent.id}
                            className="flex items-center gap-4 p-3 rounded-lg bg-[var(--card-hover)] hover:bg-[var(--border)] transition-colors cursor-pointer"
                        >
                            <div className="p-2 rounded-lg bg-[var(--border)]">
                                <agent.icon className="w-4 h-4 text-blue-400" />
                            </div>
                            <div className="flex-1">
                                <p className="font-medium text-sm">{agent.name}</p>
                                <p className="text-xs text-[var(--muted)]">{agent.description}</p>
                            </div>
                            <div className={clsx('status-dot', getStatusColor(status))} />
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
