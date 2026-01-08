'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import {
    FileText,
    Plus,
    Search,
    Check,
    Send,
    Edit,
    Trash2,
    Twitter,
    Mail,
    Newspaper,
} from 'lucide-react';

interface ContentItem {
    id: string;
    content_type: string;
    title: string;
    body: string;
    summary: string;
    status: string;
    target_platform: string;
    created_at: string;
    published_at: string | null;
}

const contentTypeIcons: Record<string, React.ElementType> = {
    tweets: Twitter,
    press_release: Newspaper,
    email: Mail,
    letter_template: Mail,
    fact_sheet: FileText,
};

const statusColors: Record<string, string> = {
    draft: 'bg-gray-500/20 text-gray-400',
    approved: 'bg-blue-500/20 text-blue-400',
    published: 'bg-green-500/20 text-green-400',
    scheduled: 'bg-purple-500/20 text-purple-400',
};

export default function ContentPage() {
    const [items, setItems] = useState<ContentItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');
    const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);

    useEffect(() => {
        fetchContent();
    }, [filter]);

    const fetchContent = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ limit: '50' });
            if (filter !== 'all') {
                params.append('status', filter);
            }
            const res = await fetch(`/api/content?${params}`);
            if (res.ok) {
                const data = await res.json();
                setItems(data);
            }
        } catch (error) {
            console.error('Failed to fetch content:', error);
        } finally {
            setLoading(false);
        }
    };

    const approveContent = async (id: string) => {
        try {
            await fetch(`/api/content/${id}/approve`, { method: 'POST' });
            fetchContent();
        } catch (error) {
            console.error('Failed to approve:', error);
        }
    };

    const publishContent = async (id: string) => {
        try {
            await fetch(`/api/content/${id}/publish`, { method: 'POST' });
            fetchContent();
        } catch (error) {
            console.error('Failed to publish:', error);
        }
    };

    const filters = ['all', 'draft', 'approved', 'published'];

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold">Content Library</h1>
                        <p className="text-[var(--muted)] mt-2">
                            Manage generated content and publishing workflow
                        </p>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-primary text-white font-medium">
                        <Plus className="w-5 h-5" />
                        Generate Content
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
                            {f}
                        </button>
                    ))}
                </div>

                {/* Content Table */}
                <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-[var(--border)]">
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">
                                    Type
                                </th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">
                                    Title
                                </th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">
                                    Status
                                </th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">
                                    Created
                                </th>
                                <th className="text-right p-4 text-sm font-medium text-[var(--muted)]">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <tr key={i} className="border-b border-[var(--border)]">
                                        <td colSpan={5} className="p-4">
                                            <div className="h-8 bg-[var(--card-hover)] rounded animate-pulse" />
                                        </td>
                                    </tr>
                                ))
                            ) : items.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="p-8 text-center text-[var(--muted)]">
                                        No content items found.
                                    </td>
                                </tr>
                            ) : (
                                items.map((item) => {
                                    const Icon = contentTypeIcons[item.content_type] || FileText;
                                    return (
                                        <tr
                                            key={item.id}
                                            className="border-b border-[var(--border)] hover:bg-[var(--card-hover)] cursor-pointer"
                                            onClick={() => setSelectedItem(item)}
                                        >
                                            <td className="p-4">
                                                <div className="flex items-center gap-2">
                                                    <Icon className="w-4 h-4 text-blue-400" />
                                                    <span className="text-sm capitalize">
                                                        {item.content_type.replace('_', ' ')}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <span className="font-medium">
                                                    {item.title || item.body.slice(0, 50) + '...'}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                <span
                                                    className={clsx(
                                                        'px-2 py-1 rounded text-xs font-medium capitalize',
                                                        statusColors[item.status]
                                                    )}
                                                >
                                                    {item.status}
                                                </span>
                                            </td>
                                            <td className="p-4 text-sm text-[var(--muted)]">
                                                {formatDistanceToNow(new Date(item.created_at), {
                                                    addSuffix: true,
                                                })}
                                            </td>
                                            <td className="p-4">
                                                <div className="flex justify-end gap-2">
                                                    {item.status === 'draft' && (
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                approveContent(item.id);
                                                            }}
                                                            className="p-2 rounded-lg hover:bg-blue-500/20 text-blue-400"
                                                            title="Approve"
                                                        >
                                                            <Check className="w-4 h-4" />
                                                        </button>
                                                    )}
                                                    {item.status === 'approved' && (
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                publishContent(item.id);
                                                            }}
                                                            className="p-2 rounded-lg hover:bg-green-500/20 text-green-400"
                                                            title="Publish"
                                                        >
                                                            <Send className="w-4 h-4" />
                                                        </button>
                                                    )}
                                                    <button className="p-2 rounded-lg hover:bg-[var(--border)] text-[var(--muted)]">
                                                        <Edit className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    );
}
