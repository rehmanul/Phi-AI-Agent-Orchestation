'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import {
    Users,
    Search,
    Filter,
    Check,
    X,
    HelpCircle,
    Phone,
    Mail,
    ExternalLink,
} from 'lucide-react';

interface Legislator {
    id: string;
    full_name: string;
    party: string;
    chamber: string;
    state: string;
    district: string;
    phone: string;
    email: string;
    website: string;
    twitter_handle: string;
    stance: string;
    committees: string[];
}

const stanceConfig: Record<string, { color: string; icon: React.ElementType; label: string }> = {
    support: { color: 'text-green-400 bg-green-500/20', icon: Check, label: 'Supporter' },
    oppose: { color: 'text-red-400 bg-red-500/20', icon: X, label: 'Opponent' },
    neutral: { color: 'text-yellow-400 bg-yellow-500/20', icon: HelpCircle, label: 'Neutral' },
    unknown: { color: 'text-gray-400 bg-gray-500/20', icon: HelpCircle, label: 'Unknown' },
};

export default function LegislatorsPage() {
    const [legislators, setLegislators] = useState<Legislator[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filters, setFilters] = useState({
        party: 'all',
        chamber: 'all',
        stance: 'all',
    });

    useEffect(() => {
        fetchLegislators();
    }, [filters]);

    const fetchLegislators = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ limit: '100' });
            if (filters.party !== 'all') params.append('party', filters.party);
            if (filters.chamber !== 'all') params.append('chamber', filters.chamber);
            if (filters.stance !== 'all') params.append('stance', filters.stance);

            const res = await fetch(`/api/legislators?${params}`);
            if (res.ok) {
                const data = await res.json();
                setLegislators(data);
            }
        } catch (error) {
            console.error('Failed to fetch legislators:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredLegislators = legislators.filter((leg) =>
        leg.full_name.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Legislators</h1>
                    <p className="text-[var(--muted)] mt-2">
                        Track legislators and their stance on wireless power policy
                    </p>
                </header>

                {/* Filters */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
                        <input
                            type="text"
                            placeholder="Search by name..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-white placeholder:text-[var(--muted)] focus:outline-none focus:border-blue-500"
                        />
                    </div>

                    <select
                        value={filters.party}
                        onChange={(e) => setFilters({ ...filters, party: e.target.value })}
                        className="px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-white"
                    >
                        <option value="all">All Parties</option>
                        <option value="D">Democrat</option>
                        <option value="R">Republican</option>
                        <option value="I">Independent</option>
                    </select>

                    <select
                        value={filters.chamber}
                        onChange={(e) => setFilters({ ...filters, chamber: e.target.value })}
                        className="px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-white"
                    >
                        <option value="all">Both Chambers</option>
                        <option value="Senate">Senate</option>
                        <option value="House">House</option>
                    </select>

                    <select
                        value={filters.stance}
                        onChange={(e) => setFilters({ ...filters, stance: e.target.value })}
                        className="px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-white"
                    >
                        <option value="all">All Stances</option>
                        <option value="support">Supporters</option>
                        <option value="oppose">Opponents</option>
                        <option value="neutral">Neutral</option>
                        <option value="unknown">Unknown</option>
                    </select>
                </div>

                {/* Table */}
                <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-[var(--border)]">
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">Name</th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">Party</th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">State</th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">Chamber</th>
                                <th className="text-left p-4 text-sm font-medium text-[var(--muted)]">Stance</th>
                                <th className="text-right p-4 text-sm font-medium text-[var(--muted)]">Contact</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                Array.from({ length: 10 }).map((_, i) => (
                                    <tr key={i} className="border-b border-[var(--border)]">
                                        <td colSpan={6} className="p-4">
                                            <div className="h-8 bg-[var(--card-hover)] rounded animate-pulse" />
                                        </td>
                                    </tr>
                                ))
                            ) : filteredLegislators.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-[var(--muted)]">
                                        <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                        <p>No legislators found.</p>
                                    </td>
                                </tr>
                            ) : (
                                filteredLegislators.map((leg) => {
                                    const stanceInfo = stanceConfig[leg.stance] || stanceConfig.unknown;
                                    const StanceIcon = stanceInfo.icon;
                                    return (
                                        <tr
                                            key={leg.id}
                                            className="border-b border-[var(--border)] hover:bg-[var(--card-hover)]"
                                        >
                                            <td className="p-4 font-medium">{leg.full_name}</td>
                                            <td className="p-4">
                                                <span
                                                    className={clsx(
                                                        'px-2 py-1 rounded text-xs font-medium',
                                                        leg.party === 'D'
                                                            ? 'bg-blue-500/20 text-blue-400'
                                                            : leg.party === 'R'
                                                                ? 'bg-red-500/20 text-red-400'
                                                                : 'bg-purple-500/20 text-purple-400'
                                                    )}
                                                >
                                                    {leg.party}
                                                </span>
                                            </td>
                                            <td className="p-4 text-[var(--muted)]">
                                                {leg.state}
                                                {leg.district && `-${leg.district}`}
                                            </td>
                                            <td className="p-4 capitalize text-[var(--muted)]">{leg.chamber}</td>
                                            <td className="p-4">
                                                <span
                                                    className={clsx(
                                                        'flex items-center gap-1 px-2 py-1 rounded text-xs font-medium w-fit',
                                                        stanceInfo.color
                                                    )}
                                                >
                                                    <StanceIcon className="w-3 h-3" />
                                                    {stanceInfo.label}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                <div className="flex justify-end gap-2">
                                                    {leg.phone && (
                                                        <a
                                                            href={`tel:${leg.phone}`}
                                                            className="p-2 rounded-lg hover:bg-[var(--border)] text-[var(--muted)] hover:text-white"
                                                        >
                                                            <Phone className="w-4 h-4" />
                                                        </a>
                                                    )}
                                                    {leg.email && (
                                                        <a
                                                            href={`mailto:${leg.email}`}
                                                            className="p-2 rounded-lg hover:bg-[var(--border)] text-[var(--muted)] hover:text-white"
                                                        >
                                                            <Mail className="w-4 h-4" />
                                                        </a>
                                                    )}
                                                    {leg.website && (
                                                        <a
                                                            href={leg.website}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="p-2 rounded-lg hover:bg-[var(--border)] text-[var(--muted)] hover:text-white"
                                                        >
                                                            <ExternalLink className="w-4 h-4" />
                                                        </a>
                                                    )}
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
