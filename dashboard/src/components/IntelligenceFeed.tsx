'use client';

import { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import {
    Newspaper,
    MessageSquare,
    Landmark,
    AlertTriangle,
    ExternalLink,
} from 'lucide-react';

interface IntelligenceItem {
    id: string;
    source_type: string;
    title: string;
    source_name: string;
    source_url: string;
    relevance_score: number;
    is_opposition: boolean;
    created_at: string;
}

const sourceIcons: Record<string, React.ElementType> = {
    news: Newspaper,
    twitter: MessageSquare,
    reddit: MessageSquare,
    legislative: Landmark,
};

export default function IntelligenceFeed() {
    const [items, setItems] = useState<IntelligenceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');

    useEffect(() => {
        fetchItems();
        const interval = setInterval(fetchItems, 30000);
        return () => clearInterval(interval);
    }, [filter]);

    const fetchItems = async () => {
        try {
            const params = new URLSearchParams({ limit: '10' });
            if (filter !== 'all') {
                params.append('source_type', filter);
            }
            const res = await fetch(`/api/intelligence?${params}`);
            if (res.ok) {
                const data = await res.json();
                setItems(data);
            }
        } catch (error) {
            console.error('Failed to fetch intelligence:', error);
        } finally {
            setLoading(false);
        }
    };

    const filters = ['all', 'news', 'twitter', 'legislative'];

    return (
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Intelligence Feed</h3>
                <div className="flex gap-2">
                    {filters.map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={clsx(
                                'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                                filter === f
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-[var(--card-hover)] text-[var(--muted)] hover:text-white'
                            )}
                        >
                            {f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-20 bg-[var(--card-hover)] rounded-lg animate-pulse" />
                    ))}
                </div>
            ) : items.length === 0 ? (
                <div className="text-center py-8 text-[var(--muted)]">
                    <p>No intelligence items yet.</p>
                    <p className="text-sm mt-2">Items will appear as the monitoring agent scans sources.</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {items.map((item) => {
                        const Icon = sourceIcons[item.source_type] || Newspaper;
                        return (
                            <div
                                key={item.id}
                                className={clsx(
                                    'p-4 rounded-lg border transition-colors hover:bg-[var(--card-hover)]',
                                    item.is_opposition
                                        ? 'border-red-500/30 bg-red-500/5'
                                        : 'border-[var(--border)]'
                                )}
                            >
                                <div className="flex items-start gap-3">
                                    <div
                                        className={clsx(
                                            'p-2 rounded-lg',
                                            item.is_opposition ? 'bg-red-500/20' : 'bg-[var(--border)]'
                                        )}
                                    >
                                        <Icon
                                            className={clsx(
                                                'w-4 h-4',
                                                item.is_opposition ? 'text-red-400' : 'text-blue-400'
                                            )}
                                        />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            {item.is_opposition && (
                                                <span className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-400 font-medium">
                                                    Opposition
                                                </span>
                                            )}
                                            <span className="text-xs text-[var(--muted)]">
                                                {item.source_name}
                                            </span>
                                        </div>
                                        <p className="font-medium text-sm line-clamp-2">{item.title}</p>
                                        <div className="flex items-center justify-between mt-2">
                                            <span className="text-xs text-[var(--muted)]">
                                                {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                                            </span>
                                            {item.source_url && (
                                                <a
                                                    href={item.source_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-blue-400 hover:text-blue-300"
                                                >
                                                    <ExternalLink className="w-3 h-3" />
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            <div className="mt-4 text-center">
                <a
                    href="/intelligence"
                    className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                >
                    View all intelligence →
                </a>
            </div>
        </div>
    );
}
