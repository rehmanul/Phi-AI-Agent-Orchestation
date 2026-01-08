'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import {
    Settings,
    Key,
    Database,
    Bell,
    Shield,
    Save,
    Eye,
    EyeOff,
    CheckCircle,
    AlertCircle,
    XCircle,
    Loader2,
    TestTube,
} from 'lucide-react';

interface Setting {
    id: string;
    key: string;
    category: string;
    display_name: string | null;
    description: string | null;
    value: string;
    is_secret: boolean;
    is_configured: boolean;
    is_required: boolean;
    updated_at: string;
}

interface SettingsCategory {
    category: string;
    settings: Setting[];
}

interface TestResult {
    key: string;
    success: boolean;
    message: string;
}

export default function SettingsPage() {
    const [categories, setCategories] = useState<SettingsCategory[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [activeCategory, setActiveCategory] = useState<string>('llm');

    // Track edited values
    const [editedValues, setEditedValues] = useState<Record<string, string>>({});
    const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
    const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
    const [testing, setTesting] = useState<Record<string, boolean>>({});

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('/api/settings/');
            if (res.ok) {
                const data: SettingsCategory[] = await res.json();
                setCategories(data);
                if (data.length > 0 && !data.find(c => c.category === activeCategory)) {
                    setActiveCategory(data[0].category);
                }
            } else {
                setError('Failed to load settings');
            }
        } catch (err) {
            setError('Failed to connect to API');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setError(null);

        try {
            // Filter out empty values
            const toUpdate: Record<string, string> = {};
            for (const [key, value] of Object.entries(editedValues)) {
                if (value && value.trim()) {
                    toUpdate[key] = value.trim();
                }
            }

            if (Object.keys(toUpdate).length === 0) {
                setSaving(false);
                return;
            }

            const res = await fetch('/api/settings/bulk', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ settings: toUpdate }),
            });

            if (res.ok) {
                const result = await res.json();
                if (result.success) {
                    setSaved(true);
                    setEditedValues({});
                    setTimeout(() => setSaved(false), 3000);
                    await fetchSettings();
                } else {
                    setError(`Some settings failed: ${result.errors.map((e: any) => e.key).join(', ')}`);
                }
            } else {
                setError('Failed to save settings');
            }
        } catch (err) {
            setError('Failed to connect to API');
        } finally {
            setSaving(false);
        }
    };

    const handleTest = async (key: string) => {
        setTesting(prev => ({ ...prev, [key]: true }));
        try {
            const res = await fetch(`/api/settings/test/${key}`, { method: 'POST' });
            if (res.ok) {
                const result: TestResult = await res.json();
                setTestResults(prev => ({ ...prev, [key]: result }));
            }
        } catch (err) {
            setTestResults(prev => ({
                ...prev,
                [key]: { key, success: false, message: 'Test request failed' },
            }));
        } finally {
            setTesting(prev => ({ ...prev, [key]: false }));
        }
    };

    const toggleSecret = (key: string) => {
        setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleValueChange = (key: string, value: string) => {
        setEditedValues(prev => ({ ...prev, [key]: value }));
    };

    const categoryInfo: Record<string, { icon: React.ElementType; label: string }> = {
        llm: { icon: Key, label: 'LLM Providers' },
        external_api: { icon: Database, label: 'External APIs' },
        communication: { icon: Bell, label: 'Communication' },
        messaging: { icon: Shield, label: 'Messaging' },
    };

    const activeSettings = categories.find(c => c.category === activeCategory)?.settings || [];

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Settings</h1>
                    <p className="text-[var(--muted)] mt-2">
                        Configure API keys and system settings. All secrets are encrypted at rest.
                    </p>
                </header>

                {error && (
                    <div className="mb-6 p-4 rounded-lg bg-red-500/20 border border-red-500/40 text-red-400">
                        <div className="flex items-center gap-2">
                            <XCircle className="w-5 h-5" />
                            <span>{error}</span>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                    </div>
                ) : (
                    <div className="flex gap-8">
                        {/* Category Navigation */}
                        <div className="w-64 space-y-2">
                            {categories.map((cat) => {
                                const info = categoryInfo[cat.category] || { icon: Settings, label: cat.category };
                                const Icon = info.icon;
                                const configuredCount = cat.settings.filter(s => s.is_configured).length;

                                return (
                                    <button
                                        key={cat.category}
                                        onClick={() => setActiveCategory(cat.category)}
                                        className={clsx(
                                            'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
                                            activeCategory === cat.category
                                                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                                                : 'bg-[var(--card)] text-[var(--muted)] hover:text-white border border-[var(--border)]'
                                        )}
                                    >
                                        <Icon className="w-5 h-5" />
                                        <div className="flex-1">
                                            <p className="font-medium">{info.label}</p>
                                            <p className="text-xs opacity-70">
                                                {configuredCount}/{cat.settings.length} configured
                                            </p>
                                        </div>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Settings Form */}
                        <div className="flex-1 bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                            <h2 className="text-xl font-semibold mb-6 capitalize">
                                {categoryInfo[activeCategory]?.label || activeCategory}
                            </h2>

                            <div className="space-y-6">
                                {activeSettings.map((setting) => {
                                    const testResult = testResults[setting.key];
                                    const isTesting = testing[setting.key];

                                    return (
                                        <div key={setting.key} className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <label className="text-sm font-medium flex items-center gap-2">
                                                    {setting.display_name || setting.key}
                                                    {setting.is_required && (
                                                        <span className="text-red-400 text-xs">Required</span>
                                                    )}
                                                    {setting.is_configured && (
                                                        <CheckCircle className="w-4 h-4 text-green-400" />
                                                    )}
                                                </label>
                                                {setting.is_configured && (
                                                    <button
                                                        onClick={() => handleTest(setting.key)}
                                                        disabled={isTesting}
                                                        className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-[var(--card-hover)] hover:bg-[var(--border)] text-[var(--muted)]"
                                                    >
                                                        {isTesting ? (
                                                            <Loader2 className="w-3 h-3 animate-spin" />
                                                        ) : (
                                                            <TestTube className="w-3 h-3" />
                                                        )}
                                                        Test
                                                    </button>
                                                )}
                                            </div>

                                            <div className="relative">
                                                <input
                                                    type={setting.is_secret && !showSecrets[setting.key] ? 'password' : 'text'}
                                                    value={editedValues[setting.key] ?? ''}
                                                    onChange={(e) => handleValueChange(setting.key, e.target.value)}
                                                    placeholder={setting.is_configured ? setting.value : 'Enter value...'}
                                                    className="w-full px-4 py-2 pr-20 rounded-lg bg-[var(--card-hover)] border border-[var(--border)] text-white placeholder:text-[var(--muted)] focus:outline-none focus:border-blue-500"
                                                />
                                                {setting.is_secret && (
                                                    <button
                                                        type="button"
                                                        onClick={() => toggleSecret(setting.key)}
                                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted)] hover:text-white"
                                                    >
                                                        {showSecrets[setting.key] ? (
                                                            <EyeOff className="w-4 h-4" />
                                                        ) : (
                                                            <Eye className="w-4 h-4" />
                                                        )}
                                                    </button>
                                                )}
                                            </div>

                                            {setting.description && (
                                                <p className="text-xs text-[var(--muted)]">{setting.description}</p>
                                            )}

                                            {testResult && (
                                                <div
                                                    className={clsx(
                                                        'text-xs px-2 py-1 rounded flex items-center gap-1',
                                                        testResult.success
                                                            ? 'bg-green-500/20 text-green-400'
                                                            : 'bg-red-500/20 text-red-400'
                                                    )}
                                                >
                                                    {testResult.success ? (
                                                        <CheckCircle className="w-3 h-3" />
                                                    ) : (
                                                        <XCircle className="w-3 h-3" />
                                                    )}
                                                    {testResult.message}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Save Button */}
                            <div className="mt-8 pt-6 border-t border-[var(--border)] flex justify-between items-center">
                                <p className="text-xs text-[var(--muted)]">
                                    {Object.keys(editedValues).filter(k => editedValues[k]).length} changes pending
                                </p>
                                <button
                                    onClick={handleSave}
                                    disabled={saving || Object.keys(editedValues).filter(k => editedValues[k]).length === 0}
                                    className={clsx(
                                        'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors',
                                        saved
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-gradient-primary text-white hover:opacity-90',
                                        (saving || Object.keys(editedValues).filter(k => editedValues[k]).length === 0) &&
                                        'opacity-50 cursor-not-allowed'
                                    )}
                                >
                                    {saved ? (
                                        <>
                                            <CheckCircle className="w-4 h-4" />
                                            Saved!
                                        </>
                                    ) : saving ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <Save className="w-4 h-4" />
                                            Save Changes
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
