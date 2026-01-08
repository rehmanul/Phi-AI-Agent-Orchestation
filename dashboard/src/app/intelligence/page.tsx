'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import {
    Radio,
    Newspaper,
    MessageSquare,
    Landmark,
    ExternalLink,
    Filter,
    Search,
    AlertTriangle,
} from 'lucide-react';

interface IntelligenceItem {
    id: string;
    source_type: string;
    source_name: string;
    source_url: string;
    title: string;
    summary: string;
    relevance_score: number;
    sentiment_score: number | null;
    is_opposition: boolean;
    requires_response: boolean;
    priority: number;
    status: string;
    created_at: string;
}

const sourceIcons: Record<string, React.ElementType> = {
    news: Newspaper,
    twitter: MessageSquare,
    reddit: MessageSquare,
    legislative: Landmark,
};

export default function IntelligencePage() {
    const [items, setItems] = useState<IntelligenceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');
    const [search, setSearch] = useState('');
    const [selectedItem, setSelectedItem] = useState<IntelligenceItem | null>(null);

    useEffect(() => {
        fetchItems();
    }, [filter]);

    const fetchItems = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ limit: '50' });
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

    const filteredItems = items.filter((item) =>
        item.title?.toLowerCase().includes(search.toLowerCase())
    );

    const filters = [
        { id: 'all', label: 'All', icon: Radio },
        { id: 'news', label: 'News', icon: Newspaper },
        { id: 'twitter', label: 'Twitter', icon: MessageSquare },
        { id: 'legislative', label: 'Legislative', icon: Landmark },
    ];

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Intelligence Feed</h1>
                    <p className="text-[var(--muted)] mt-2">
                        Real-time monitoring of legislative, news, and social sources
                    </p>
                </header>

                {/* Filters */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="flex gap-2">
                        {filters.map((f) => (
                            <button
                                key={f.id}
                                onClick={() => setFilter(f.id)}
                                className={clsx(
                                    'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
                                    filter === f.id
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-[var(--card)] text-[var(--muted)] hover:text-white border border-[var(--border)]'
                                )}
                            >
                                <f.icon className="w-4 h-4" />
                                {f.label}
                            </button>
                        ))}
                    </div>

                    <div className="flex-1 max-w-md ml-auto">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                            <input
                                type="text"
                                placeholder="Search intelligence..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-white placeholder:text-[var(--muted)] focus:outline-none focus:border-blue-500"
                            />
                        </div>
                    </div>
                </div>

                {/* Items Grid */}
                <div className="grid grid-cols-2 gap-4">
                    {loading ? (
                        Array.from({ length: 6 }).map((_, i) => (
                            <div
                                key={i}
                                className="h-32 bg-[var(--card)] rounded-xl animate-pulse"
                            />
                        ))
                    ) : filteredItems.length === 0 ? (
                        <div className="col-span-2 text-center py-12 text-[var(--muted)]">
                            <Radio className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>No intelligence items found.</p>
                        </div>
                    ) : (
                        filteredItems.map((item) => {
                            const Icon = sourceIcons[item.source_type] || Radio;
                            return (
                                <div
                                    key={item.id}
                                    onClick={() => setSelectedItem(item)}
                                    className={clsx(
                                        'p-5 rounded-xl border cursor-pointer transition-all hover:scale-[1.02]',
                                        'bg-[var(--card)]',
                                        item.is_opposition
                                            ? 'border-red-500/40'
                                            : 'border-[var(--border)] hover:border-blue-500/40'
                                    )}
                                >
                                    <div className="flex items-start gap-4">
                                        <div
                                            className={clsx(
                                                'p-3 rounded-lg',
                                                item.is_opposition ? 'bg-red-500/20' : 'bg-blue-500/20'
                                            )}
                                        >
                                            <Icon
                                                className={clsx(
                                                    'w-5 h-5',
                                                    item.is_opposition ? 'text-red-400' : 'text-blue-400'
                                                )}
                                            />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-2">
                                                {item.is_opposition && (
                                                    <span className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-400 font-medium flex items-center gap-1">
                                                        <AlertTriangle className="w-3 h-3" />
                                                        Opposition
                                                    </span>
                                                )}
                                                <span className="text-xs text-[var(--muted)]">
                                                    {item.source_name}
                                                </span>
                                            </div>
                                            <h3 className="font-medium line-clamp-2 mb-2">{item.title}</h3>
                                            <div className="flex items-center justify-between text-xs text-[var(--muted)]">
                                                <span>
                                                    {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                                                </span>
                                                <span
                                                    className={clsx(
                                                        'px-2 py-0.5 rounded font-medium',
                                                        item.relevance_score >= 0.7
                                                            ? 'bg-green-500/20 text-green-400'
                                                            : item.relevance_score >= 0.4
                                                                ? 'bg-yellow-500/20 text-yellow-400'
                                                                : 'bg-gray-500/20 text-gray-400'
                                                    )}
                                                >
                                                    {Math.round(item.relevance_score * 100)}% relevant
                                                </span>
                                            </div>
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
