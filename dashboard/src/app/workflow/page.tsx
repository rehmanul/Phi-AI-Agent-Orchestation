'use client';

import { useState, useEffect, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import {
    Search,
    FileText,
    Building2,
    Users,
    Gavel,
    Vote,
    CheckCircle2,
    ChevronRight,
    Lock,
    Unlock,
    AlertCircle,
    Play,
    RefreshCw,
    Loader2,
} from 'lucide-react';

interface StateInfo {
    state_id: string;
    name: string;
    icon: string;
    description: string;
    status: string;
    index: number;
}

interface GateInfo {
    gate_id: string;
    name: string;
    from_state: string;
    to_state: string;
    status: string;
    is_active: boolean;
    approved_at?: string;
    approved_by?: string;
}

interface CurrentState {
    current_state: string;
    state_name: string;
    state_icon: string;
    state_description: string;
    state_index: number;
    total_states: number;
    can_advance: boolean;
    pending_gate?: string;
}

const ICONS: Record<string, React.ReactNode> = {
    'PRE_EVT': <Search className="w-6 h-6" />,
    'INTRO_EVT': <FileText className="w-6 h-6" />,
    'COMM_EVT': <Building2 className="w-6 h-6" />,
    'FLOOR_EVT': <Gavel className="w-6 h-6" />,
    'FINAL_EVT': <Vote className="w-6 h-6" />,
    'IMPL_EVT': <CheckCircle2 className="w-6 h-6" />,
};

export default function WorkflowPage() {
    const [states, setStates] = useState<StateInfo[]>([]);
    const [currentState, setCurrentState] = useState<CurrentState | null>(null);
    const [gates, setGates] = useState<GateInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [approving, setApproving] = useState<string | null>(null);
    const [advancing, setAdvancing] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            const [statesRes, currentRes, gatesRes] = await Promise.all([
                fetch('/api/legislative/states'),
                fetch('/api/legislative/state'),
                fetch('/api/legislative/gates'),
            ]);

            if (statesRes.ok) {
                const data = await statesRes.json();
                setStates(data.states);
            }
            if (currentRes.ok) {
                const data = await currentRes.json();
                setCurrentState(data);
            }
            if (gatesRes.ok) {
                const data = await gatesRes.json();
                setGates(data.gates);
            }
        } catch (error) {
            console.error('Failed to fetch workflow data:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const approveGate = async (gateId: string) => {
        setApproving(gateId);
        try {
            const res = await fetch(`/api/legislative/gates/${gateId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved_by: 'Dashboard User' }),
            });

            if (res.ok) {
                await fetchData();
            }
        } catch (error) {
            console.error('Failed to approve gate:', error);
        } finally {
            setApproving(null);
        }
    };

    const advanceState = async () => {
        setAdvancing(true);
        try {
            const res = await fetch('/api/legislative/advance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ approved_by: 'Dashboard User' }),
            });

            if (res.ok) {
                await fetchData();
            }
        } catch (error) {
            console.error('Failed to advance state:', error);
        } finally {
            setAdvancing(false);
        }
    };

    const resetWorkflow = async () => {
        if (!confirm('Reset workflow to initial state?')) return;

        try {
            await fetch('/api/legislative/reset', { method: 'POST' });
            await fetchData();
        } catch (error) {
            console.error('Failed to reset workflow:', error);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'bg-green-500';
            case 'current':
                return 'bg-blue-500 animate-pulse';
            default:
                return 'bg-gray-600';
        }
    };

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Legislative Workflow</h1>
                        <p className="text-[var(--muted)] mt-2">
                            Track progress through the legislative spine
                        </p>
                    </div>
                    <button
                        onClick={resetWorkflow}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] hover:bg-[var(--card-hover)] text-sm"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Reset
                    </button>
                </header>

                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                    </div>
                ) : (
                    <>
                        {/* Legislative Spine Timeline */}
                        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6 mb-8">
                            <h2 className="text-lg font-semibold mb-6">Legislative Spine</h2>

                            <div className="flex items-center justify-between relative">
                                {/* Progress line */}
                                <div className="absolute top-8 left-0 right-0 h-1 bg-[var(--border)]" />
                                <div
                                    className="absolute top-8 left-0 h-1 bg-blue-500 transition-all duration-500"
                                    style={{
                                        width: `${currentState ? (currentState.state_index / (states.length - 1)) * 100 : 0}%`,
                                    }}
                                />

                                {states.map((state, index) => (
                                    <div key={state.state_id} className="flex flex-col items-center z-10">
                                        <div
                                            className={clsx(
                                                'w-16 h-16 rounded-full flex items-center justify-center border-4 transition-all',
                                                state.status === 'completed' && 'bg-green-500 border-green-400 text-white',
                                                state.status === 'current' && 'bg-blue-500 border-blue-400 text-white ring-4 ring-blue-500/30',
                                                state.status === 'upcoming' && 'bg-[var(--card)] border-[var(--border)] text-[var(--muted)]'
                                            )}
                                        >
                                            {ICONS[state.state_id] || <span className="text-2xl">{state.icon}</span>}
                                        </div>
                                        <div className="mt-3 text-center">
                                            <p className={clsx(
                                                'font-semibold text-sm',
                                                state.status === 'current' && 'text-blue-400',
                                                state.status === 'upcoming' && 'text-[var(--muted)]'
                                            )}>
                                                {state.name}
                                            </p>
                                            <p className="text-xs text-[var(--muted)] mt-1 max-w-[120px]">
                                                {state.description}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Current State + Gates */}
                        <div className="grid grid-cols-2 gap-6">
                            {/* Current State */}
                            <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                                <h2 className="text-lg font-semibold mb-4">Current State</h2>
                                {currentState && (
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-4">
                                            <div className="w-14 h-14 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                                                {ICONS[currentState.current_state] || <span className="text-2xl">{currentState.state_icon}</span>}
                                            </div>
                                            <div>
                                                <h3 className="text-xl font-bold">{currentState.state_name}</h3>
                                                <p className="text-[var(--muted)]">{currentState.state_description}</p>
                                            </div>
                                        </div>

                                        <div className="bg-[var(--card-hover)] rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm text-[var(--muted)]">Progress</span>
                                                <span className="font-semibold">
                                                    {currentState.state_index + 1} / {currentState.total_states}
                                                </span>
                                            </div>
                                        </div>

                                        {currentState.pending_gate && (
                                            <div className="flex items-center gap-2 text-yellow-400 bg-yellow-500/10 rounded-lg p-3">
                                                <AlertCircle className="w-5 h-5" />
                                                <span className="text-sm">Pending approval: {currentState.pending_gate}</span>
                                            </div>
                                        )}

                                        <button
                                            onClick={advanceState}
                                            disabled={!currentState.can_advance || advancing}
                                            className={clsx(
                                                'w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors',
                                                currentState.can_advance
                                                    ? 'bg-blue-500 hover:bg-blue-600 text-white'
                                                    : 'bg-[var(--card-hover)] text-[var(--muted)] cursor-not-allowed'
                                            )}
                                        >
                                            {advancing ? (
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                            ) : (
                                                <>
                                                    <Play className="w-5 h-5" />
                                                    Advance to Next State
                                                </>
                                            )}
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Review Gates */}
                            <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                                <h2 className="text-lg font-semibold mb-4">Human Review Gates</h2>
                                <div className="space-y-3">
                                    {gates.map((gate) => (
                                        <div
                                            key={gate.gate_id}
                                            className={clsx(
                                                'p-4 rounded-lg border transition-colors',
                                                gate.is_active && gate.status === 'pending'
                                                    ? 'border-yellow-500 bg-yellow-500/10'
                                                    : gate.status === 'approved'
                                                        ? 'border-green-500/50 bg-green-500/10'
                                                        : 'border-[var(--border)]'
                                            )}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    {gate.status === 'approved' ? (
                                                        <Unlock className="w-5 h-5 text-green-400" />
                                                    ) : (
                                                        <Lock className="w-5 h-5 text-[var(--muted)]" />
                                                    )}
                                                    <div>
                                                        <p className="font-medium">{gate.name}</p>
                                                        <p className="text-xs text-[var(--muted)]">
                                                            {gate.from_state} → {gate.to_state}
                                                        </p>
                                                    </div>
                                                </div>

                                                {gate.is_active && gate.status === 'pending' && (
                                                    <button
                                                        onClick={() => approveGate(gate.gate_id)}
                                                        disabled={approving === gate.gate_id}
                                                        className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                                                    >
                                                        {approving === gate.gate_id ? (
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                        ) : (
                                                            <CheckCircle2 className="w-4 h-4" />
                                                        )}
                                                        Approve
                                                    </button>
                                                )}

                                                {gate.status === 'approved' && (
                                                    <span className="text-xs text-green-400">
                                                        ✓ Approved
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}
