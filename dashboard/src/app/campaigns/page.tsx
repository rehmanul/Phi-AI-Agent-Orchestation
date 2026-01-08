'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import {
    Plus,
    Search,
    Zap,
    MoreVertical,
    Edit,
    Trash2,
    Play,
    Pause,
} from 'lucide-react';

interface Campaign {
    id: string;
    name: string;
    description: string;
    goal: string;
    status: string;
    keywords: string[];
    created_at: string;
    updated_at: string;
}

export default function CampaignsPage() {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);

    useEffect(() => {
        fetchCampaigns();
    }, []);

    const fetchCampaigns = async () => {
        try {
            const res = await fetch('/api/campaigns');
            if (res.ok) {
                const data = await res.json();
                setCampaigns(data);
            }
        } catch (error) {
            console.error('Failed to fetch campaigns:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'bg-green-500/20 text-green-400';
            case 'paused':
                return 'bg-yellow-500/20 text-yellow-400';
            case 'completed':
                return 'bg-blue-500/20 text-blue-400';
            case 'archived':
                return 'bg-gray-500/20 text-gray-400';
            default:
                return 'bg-gray-500/20 text-gray-400';
        }
    };

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold">Campaigns</h1>
                        <p className="text-[var(--muted)] mt-2">
                            Manage your advocacy campaigns and goals
                        </p>
                    </div>
                    <button
                        onClick={() => setShowCreate(true)}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-primary text-white font-medium hover:opacity-90 transition-opacity"
                    >
                        <Plus className="w-5 h-5" />
                        New Campaign
                    </button>
                </header>

                {/* Campaigns Grid */}
                {loading ? (
                    <div className="grid grid-cols-2 gap-6">
                        {[1, 2, 3, 4].map((i) => (
                            <div
                                key={i}
                                className="h-48 bg-[var(--card)] rounded-xl animate-pulse"
                            />
                        ))}
                    </div>
                ) : campaigns.length === 0 ? (
                    <div className="text-center py-16">
                        <Zap className="w-16 h-16 mx-auto mb-4 text-[var(--muted)] opacity-50" />
                        <h3 className="text-xl font-semibold mb-2">No campaigns yet</h3>
                        <p className="text-[var(--muted)] mb-6">
                            Create your first campaign to start organizing your advocacy efforts.
                        </p>
                        <button
                            onClick={() => setShowCreate(true)}
                            className="px-6 py-3 rounded-lg bg-gradient-primary text-white font-medium"
                        >
                            Create Campaign
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-6">
                        {campaigns.map((campaign) => (
                            <div
                                key={campaign.id}
                                className="p-6 rounded-xl bg-[var(--card)] border border-[var(--border)] hover:border-blue-500/40 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-3 rounded-lg bg-gradient-primary">
                                            <Zap className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-lg">{campaign.name}</h3>
                                            <span
                                                className={clsx(
                                                    'text-xs px-2 py-0.5 rounded font-medium',
                                                    getStatusColor(campaign.status)
                                                )}
                                            >
                                                {campaign.status}
                                            </span>
                                        </div>
                                    </div>
                                    <button className="p-2 rounded-lg hover:bg-[var(--card-hover)]">
                                        <MoreVertical className="w-4 h-4 text-[var(--muted)]" />
                                    </button>
                                </div>

                                <p className="text-[var(--muted)] text-sm mb-4 line-clamp-2">
                                    {campaign.description || 'No description provided.'}
                                </p>

                                {campaign.keywords.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mb-4">
                                        {campaign.keywords.slice(0, 4).map((kw, i) => (
                                            <span
                                                key={i}
                                                className="px-2 py-1 rounded text-xs bg-blue-500/10 text-blue-400"
                                            >
                                                {kw}
                                            </span>
                                        ))}
                                        {campaign.keywords.length > 4 && (
                                            <span className="text-xs text-[var(--muted)]">
                                                +{campaign.keywords.length - 4} more
                                            </span>
                                        )}
                                    </div>
                                )}

                                <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
                                    <span className="text-xs text-[var(--muted)]">
                                        Updated{' '}
                                        {formatDistanceToNow(new Date(campaign.updated_at), {
                                            addSuffix: true,
                                        })}
                                    </span>
                                    <div className="flex gap-2">
                                        <button className="p-2 rounded-lg hover:bg-[var(--card-hover)] text-[var(--muted)] hover:text-white">
                                            <Edit className="w-4 h-4" />
                                        </button>
                                        {campaign.status === 'active' ? (
                                            <button className="p-2 rounded-lg hover:bg-yellow-500/20 text-yellow-400">
                                                <Pause className="w-4 h-4" />
                                            </button>
                                        ) : (
                                            <button className="p-2 rounded-lg hover:bg-green-500/20 text-green-400">
                                                <Play className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
