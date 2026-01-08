'use client';

import { useState, useEffect, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import {
    Bot,
    Play,
    CheckCircle,
    Clock,
    AlertCircle,
    FileText,
    Loader2,
    RefreshCw,
    Zap,
} from 'lucide-react';

interface AgentInfo {
    agent_id: string;
    agent_type: string;
    name: string;
    icon: string;
    description: string;
    status: string;
    spawned_at?: string;
    completed_at?: string;
    artifacts: string[];
}

interface AgentsByType {
    [type: string]: AgentInfo[];
}

const TYPE_COLORS: Record<string, string> = {
    intelligence: 'text-blue-400 bg-blue-500/20',
    drafting: 'text-purple-400 bg-purple-500/20',
    execution: 'text-green-400 bg-green-500/20',
    learning: 'text-yellow-400 bg-yellow-500/20',
};

export default function OrchestrationPage() {
    const [agents, setAgents] = useState<AgentInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentState, setCurrentState] = useState<string>('');
    const [spawning, setSpawning] = useState<Set<string>>(new Set());

    const fetchData = useCallback(async () => {
        try {
            // Get current state
            const stateRes = await fetch('/api/legislative/state');
            if (stateRes.ok) {
                const data = await stateRes.json();
                setCurrentState(data.current_state);
            }

            // Get agents
            const agentsRes = await fetch('/api/orchestration/agents');
            if (agentsRes.ok) {
                const data = await agentsRes.json();
                setAgents(data.agents);
            }
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const spawnAgent = async (agentId: string) => {
        setSpawning((prev) => new Set([...prev, agentId]));
        try {
            const res = await fetch('/api/orchestration/spawn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_ids: [agentId] }),
            });

            if (res.ok) {
                await fetchData();
            }
        } catch (error) {
            console.error('Failed to spawn agent:', error);
        } finally {
            setSpawning((prev) => {
                const next = new Set(prev);
                next.delete(agentId);
                return next;
            });
        }
    };

    const spawnAll = async (type: string) => {
        const agentsOfType = agents.filter(
            (a) => a.agent_type === type && a.status === 'idle'
        );
        for (const agent of agentsOfType) {
            await spawnAgent(agent.agent_id);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'running':
                return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />;
            case 'completed':
                return <CheckCircle className="w-4 h-4 text-green-400" />;
            case 'error':
                return <AlertCircle className="w-4 h-4 text-red-400" />;
            default:
                return <Clock className="w-4 h-4 text-[var(--muted)]" />;
        }
    };

    // Group agents by type
    const agentsByType = agents.reduce<AgentsByType>((acc, agent) => {
        const type = agent.agent_type || 'unknown';
        if (!acc[type]) acc[type] = [];
        acc[type].push(agent);
        return acc;
    }, {});

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Agent Orchestration</h1>
                        <p className="text-[var(--muted)] mt-2">
                            Spawn and monitor AI agents • Current State: <span className="text-blue-400 font-medium">{currentState}</span>
                        </p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] hover:bg-[var(--card-hover)] text-sm"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                </header>

                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-6">
                        {Object.entries(agentsByType).map(([type, typeAgents]) => (
                            <div
                                key={type}
                                className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden"
                            >
                                <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
                                    <div className="flex items-center gap-3">
                                        <div className={clsx('p-2 rounded-lg', TYPE_COLORS[type] || 'bg-gray-500/20')}>
                                            <Bot className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h2 className="font-semibold capitalize">{type} Agents</h2>
                                            <p className="text-xs text-[var(--muted)]">
                                                {typeAgents.filter((a) => a.status === 'running').length} running •{' '}
                                                {typeAgents.filter((a) => a.status === 'completed').length} completed
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => spawnAll(type)}
                                        className="px-3 py-1.5 bg-[var(--card-hover)] hover:bg-blue-500/20 rounded-lg text-sm flex items-center gap-1"
                                    >
                                        <Zap className="w-4 h-4" />
                                        Spawn All
                                    </button>
                                </div>

                                <div className="divide-y divide-[var(--border)]">
                                    {typeAgents.map((agent) => (
                                        <div
                                            key={agent.agent_id}
                                            className="p-4 flex items-center justify-between hover:bg-[var(--card-hover)]"
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">{agent.icon}</span>
                                                <div>
                                                    <p className="font-medium">{agent.name}</p>
                                                    <p className="text-xs text-[var(--muted)]">{agent.description}</p>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-3">
                                                <div className="flex items-center gap-1.5">
                                                    {getStatusIcon(agent.status)}
                                                    <span className="text-xs text-[var(--muted)] capitalize">
                                                        {agent.status}
                                                    </span>
                                                </div>

                                                {agent.artifacts.length > 0 && (
                                                    <span className="flex items-center gap-1 text-xs text-green-400">
                                                        <FileText className="w-3 h-3" />
                                                        {agent.artifacts.length}
                                                    </span>
                                                )}

                                                {agent.status === 'idle' && (
                                                    <button
                                                        onClick={() => spawnAgent(agent.agent_id)}
                                                        disabled={spawning.has(agent.agent_id)}
                                                        className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm flex items-center gap-1"
                                                    >
                                                        {spawning.has(agent.agent_id) ? (
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                        ) : (
                                                            <>
                                                                <Play className="w-4 h-4" />
                                                                Spawn
                                                            </>
                                                        )}
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
