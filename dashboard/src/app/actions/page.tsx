'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import {
    Plus,
    Phone,
    Mail,
    Users,
    Megaphone,
    Calendar,
    Clock,
    CheckCircle,
    Circle,
    PlayCircle,
    XCircle,
} from 'lucide-react';

interface Action {
    id: string;
    campaign_id: string | null;
    action_type: string;
    title: string;
    description: string | null;
    instructions: string | null;
    priority: number;
    status: string;
    assigned_to: string | null;
    due_date: string | null;
    estimated_time_hours: number | null;
    created_at: string;
    completed_at: string | null;
}

const actionTypeIcons: Record<string, React.ElementType> = {
    phone_bank: Phone,
    letter_campaign: Mail,
    lobby_day: Users,
    press_event: Megaphone,
    social_blitz: Megaphone,
    general: Calendar,
};

const statusConfig: Record<string, { color: string; icon: React.ElementType }> = {
    pending: { color: 'text-yellow-400 bg-yellow-500/20', icon: Circle },
    in_progress: { color: 'text-blue-400 bg-blue-500/20', icon: PlayCircle },
    completed: { color: 'text-green-400 bg-green-500/20', icon: CheckCircle },
    cancelled: { color: 'text-gray-400 bg-gray-500/20', icon: XCircle },
};

export default function ActionsPage() {
    const [actions, setActions] = useState<Action[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');

    useEffect(() => {
        fetchActions();
    }, [filter]);

    const fetchActions = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ limit: '50' });
            if (filter !== 'all') {
                params.append('status', filter);
            }
            const res = await fetch(`/api/actions?${params}`);
            if (res.ok) {
                const data = await res.json();
                setActions(data);
            }
        } catch (error) {
            console.error('Failed to fetch actions:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateStatus = async (id: string, newStatus: string) => {
        try {
            await fetch(`/api/actions/${id}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus }),
            });
            fetchActions();
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    };

    const filters = ['all', 'pending', 'in_progress', 'completed'];

    const getPriorityColor = (priority: number) => {
        if (priority >= 8) return 'border-l-red-500';
        if (priority >= 5) return 'border-l-yellow-500';
        return 'border-l-blue-500';
    };

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold">Actions</h1>
                        <p className="text-[var(--muted)] mt-2">
                            Tactical actions and campaign tasks
                        </p>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-primary text-white font-medium">
                        <Plus className="w-5 h-5" />
                        New Action
                    </button>
                </header>

                {/* Filters */}
                <div className="flex gap-2 mb-6">
                    {filters.map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={clsx(
                                'px-4 py-2 rounded-lg font-medium transition-colors capitalize',
                                filter === f
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-[var(--card)] text-[var(--muted)] hover:text-white border border-[var(--border)]'
                            )}
                        >
                            {f.replace('_', ' ')}
                        </button>
                    ))}
                </div>

                {/* Actions List */}
                <div className="space-y-4">
                    {loading ? (
                        Array.from({ length: 5 }).map((_, i) => (
                            <div
                                key={i}
                                className="h-24 bg-[var(--card)] rounded-xl animate-pulse"
                            />
                        ))
                    ) : actions.length === 0 ? (
                        <div className="text-center py-16 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                            <Calendar className="w-16 h-16 mx-auto mb-4 text-[var(--muted)] opacity-50" />
                            <h3 className="text-xl font-semibold mb-2">No actions found</h3>
                            <p className="text-[var(--muted)]">
                                Actions will appear here as they are generated by the Tactics Agent.
                            </p>
                        </div>
                    ) : (
                        actions.map((action) => {
                            const Icon = actionTypeIcons[action.action_type] || Calendar;
                            const statusInfo = statusConfig[action.status] || statusConfig.pending;
                            const StatusIcon = statusInfo.icon;

                            return (
                                <div
                                    key={action.id}
                                    className={clsx(
                                        'p-5 rounded-xl bg-[var(--card)] border border-[var(--border)] border-l-4',
                                        getPriorityColor(action.priority)
                                    )}
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="p-3 rounded-lg bg-[var(--card-hover)]">
                                            <Icon className="w-5 h-5 text-blue-400" />
                                        </div>

                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <h3 className="font-semibold">{action.title}</h3>
                                                <span
                                                    className={clsx(
                                                        'flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium capitalize',
                                                        statusInfo.color
                                                    )}
                                                >
                                                    <StatusIcon className="w-3 h-3" />
                                                    {action.status.replace('_', ' ')}
                                                </span>
                                                <span className="text-xs text-[var(--muted)] capitalize">
                                                    {action.action_type.replace('_', ' ')}
                                                </span>
                                            </div>

                                            {action.description && (
                                                <p className="text-sm text-[var(--muted)] mb-3 line-clamp-2">
                                                    {action.description}
                                                </p>
                                            )}

                                            <div className="flex items-center gap-6 text-sm text-[var(--muted)]">
                                                <span className="flex items-center gap-1">
                                                    <Clock className="w-4 h-4" />
                                                    {action.estimated_time_hours
                                                        ? `${action.estimated_time_hours}h estimated`
                                                        : 'No estimate'}
                                                </span>
                                                {action.due_date && (
                                                    <span>Due: {new Date(action.due_date).toLocaleDateString()}</span>
                                                )}
                                                <span>
                                                    Created{' '}
                                                    {formatDistanceToNow(new Date(action.created_at), {
                                                        addSuffix: true,
                                                    })}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="flex gap-2">
                                            {action.status === 'pending' && (
                                                <button
                                                    onClick={() => updateStatus(action.id, 'in_progress')}
                                                    className="px-3 py-1 rounded-lg text-sm bg-blue-500/20 text-blue-400 hover:bg-blue-500/30"
                                                >
                                                    Start
                                                </button>
                                            )}
                                            {action.status === 'in_progress' && (
                                                <button
                                                    onClick={() => updateStatus(action.id, 'completed')}
                                                    className="px-3 py-1 rounded-lg text-sm bg-green-500/20 text-green-400 hover:bg-green-500/30"
                                                >
                                                    Complete
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </main>
        </div>
    );
}
