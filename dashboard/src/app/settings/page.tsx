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
} from 'lucide-react';

interface ConfigSection {
    id: string;
    title: string;
    icon: React.ElementType;
    description: string;
}

const sections: ConfigSection[] = [
    { id: 'api-keys', title: 'API Keys', icon: Key, description: 'Configure external API credentials' },
    { id: 'database', title: 'Database', icon: Database, description: 'Database connection settings' },
    { id: 'notifications', title: 'Notifications', icon: Bell, description: 'Alert and notification preferences' },
    { id: 'security', title: 'Security', icon: Shield, description: 'Authentication and access control' },
];

export default function SettingsPage() {
    const [activeSection, setActiveSection] = useState('api-keys');
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

    // API Keys state
    const [apiKeys, setApiKeys] = useState({
        openai_key: '',
        anthropic_key: '',
        congress_key: '',
        twitter_token: '',
        reddit_client_id: '',
        reddit_secret: '',
        newsapi_key: '',
        sendgrid_key: '',
        twilio_sid: '',
        twilio_token: '',
    });

    // Notification settings
    const [notifications, setNotifications] = useState({
        email_alerts: true,
        opposition_alerts: true,
        bill_updates: true,
        daily_digest: true,
        weekly_report: false,
    });

    const toggleSecret = (key: string) => {
        setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // In production, this would call the API to save settings
            await new Promise(resolve => setTimeout(resolve, 1000));
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } finally {
            setSaving(false);
        }
    };

    const renderApiKeyInput = (key: string, label: string, placeholder: string) => (
        <div key={key} className="flex items-center gap-4">
            <label className="w-48 text-sm font-medium">{label}</label>
            <div className="flex-1 relative">
                <input
                    type={showSecrets[key] ? 'text' : 'password'}
                    value={apiKeys[key as keyof typeof apiKeys]}
                    onChange={(e) => setApiKeys(prev => ({ ...prev, [key]: e.target.value }))}
                    placeholder={placeholder}
                    className="w-full px-4 py-2 pr-10 rounded-lg bg-[var(--card-hover)] border border-[var(--border)] text-white placeholder:text-[var(--muted)] focus:outline-none focus:border-blue-500"
                />
                <button
                    type="button"
                    onClick={() => toggleSecret(key)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted)] hover:text-white"
                >
                    {showSecrets[key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
            </div>
        </div>
    );

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Settings</h1>
                    <p className="text-[var(--muted)] mt-2">
                        Configure system settings and credentials
                    </p>
                </header>

                <div className="flex gap-8">
                    {/* Sidebar Navigation */}
                    <div className="w-64 space-y-2">
                        {sections.map((section) => (
                            <button
                                key={section.id}
                                onClick={() => setActiveSection(section.id)}
                                className={clsx(
                                    'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
                                    activeSection === section.id
                                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                                        : 'bg-[var(--card)] text-[var(--muted)] hover:text-white border border-[var(--border)]'
                                )}
                            >
                                <section.icon className="w-5 h-5" />
                                <div>
                                    <p className="font-medium">{section.title}</p>
                                    <p className="text-xs opacity-70">{section.description}</p>
                                </div>
                            </button>
                        ))}
                    </div>

                    {/* Settings Content */}
                    <div className="flex-1 bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                        {activeSection === 'api-keys' && (
                            <div>
                                <h2 className="text-xl font-semibold mb-6">API Keys</h2>
                                <p className="text-sm text-[var(--muted)] mb-6">
                                    Configure API credentials for external services. These are stored securely and used by the agents.
                                </p>

                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-sm font-medium text-[var(--muted)] mb-4 uppercase">LLM Providers</h3>
                                        <div className="space-y-4">
                                            {renderApiKeyInput('openai_key', 'OpenAI API Key', 'sk-...')}
                                            {renderApiKeyInput('anthropic_key', 'Anthropic API Key', 'sk-ant-...')}
                                        </div>
                                    </div>

                                    <div className="border-t border-[var(--border)] pt-6">
                                        <h3 className="text-sm font-medium text-[var(--muted)] mb-4 uppercase">Data Sources</h3>
                                        <div className="space-y-4">
                                            {renderApiKeyInput('congress_key', 'Congress.gov API Key', 'Your API key')}
                                            {renderApiKeyInput('twitter_token', 'Twitter Bearer Token', 'Bearer token')}
                                            {renderApiKeyInput('newsapi_key', 'NewsAPI Key', 'Your API key')}
                                        </div>
                                    </div>

                                    <div className="border-t border-[var(--border)] pt-6">
                                        <h3 className="text-sm font-medium text-[var(--muted)] mb-4 uppercase">Communication</h3>
                                        <div className="space-y-4">
                                            {renderApiKeyInput('sendgrid_key', 'SendGrid API Key', 'SG...')}
                                            {renderApiKeyInput('twilio_sid', 'Twilio Account SID', 'AC...')}
                                            {renderApiKeyInput('twilio_token', 'Twilio Auth Token', 'Your token')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeSection === 'database' && (
                            <div>
                                <h2 className="text-xl font-semibold mb-6">Database Settings</h2>
                                <p className="text-sm text-[var(--muted)] mb-6">
                                    Database connections are configured via environment variables. Current connection status:
                                </p>

                                <div className="space-y-4">
                                    <div className="p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <Database className="w-5 h-5 text-blue-400" />
                                                <span className="font-medium">PostgreSQL</span>
                                            </div>
                                            <span className="flex items-center gap-2 text-green-400 text-sm">
                                                <CheckCircle className="w-4 h-4" />
                                                Connected
                                            </span>
                                        </div>
                                        <p className="text-xs text-[var(--muted)] mt-2 ml-8">
                                            Primary database for campaigns, intelligence, content
                                        </p>
                                    </div>

                                    <div className="p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <Database className="w-5 h-5 text-red-400" />
                                                <span className="font-medium">Redis</span>
                                            </div>
                                            <span className="flex items-center gap-2 text-yellow-400 text-sm">
                                                <AlertCircle className="w-4 h-4" />
                                                Optional
                                            </span>
                                        </div>
                                        <p className="text-xs text-[var(--muted)] mt-2 ml-8">
                                            Caching and message queuing (configure REDIS_DSN)
                                        </p>
                                    </div>

                                    <div className="p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <Database className="w-5 h-5 text-purple-400" />
                                                <span className="font-medium">Kafka</span>
                                            </div>
                                            <span className="flex items-center gap-2 text-yellow-400 text-sm">
                                                <AlertCircle className="w-4 h-4" />
                                                Optional
                                            </span>
                                        </div>
                                        <p className="text-xs text-[var(--muted)] mt-2 ml-8">
                                            Inter-agent messaging (configure KAFKA_BOOTSTRAP_SERVERS)
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeSection === 'notifications' && (
                            <div>
                                <h2 className="text-xl font-semibold mb-6">Notification Settings</h2>
                                <p className="text-sm text-[var(--muted)] mb-6">
                                    Configure how and when you receive alerts from the system.
                                </p>

                                <div className="space-y-4">
                                    {Object.entries(notifications).map(([key, value]) => (
                                        <div
                                            key={key}
                                            className="flex items-center justify-between p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]"
                                        >
                                            <div>
                                                <p className="font-medium capitalize">{key.replace(/_/g, ' ')}</p>
                                                <p className="text-xs text-[var(--muted)]">
                                                    {key === 'email_alerts' && 'Receive email notifications for important events'}
                                                    {key === 'opposition_alerts' && 'Get notified when opposition content is detected'}
                                                    {key === 'bill_updates' && 'Alerts when tracked bills have status changes'}
                                                    {key === 'daily_digest' && 'Daily summary of campaign activity'}
                                                    {key === 'weekly_report' && 'Weekly performance report'}
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => setNotifications(prev => ({ ...prev, [key]: !value }))}
                                                className={clsx(
                                                    'w-12 h-6 rounded-full transition-colors relative',
                                                    value ? 'bg-blue-500' : 'bg-[var(--border)]'
                                                )}
                                            >
                                                <div
                                                    className={clsx(
                                                        'w-5 h-5 rounded-full bg-white absolute top-0.5 transition-transform',
                                                        value ? 'translate-x-6' : 'translate-x-0.5'
                                                    )}
                                                />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeSection === 'security' && (
                            <div>
                                <h2 className="text-xl font-semibold mb-6">Security Settings</h2>
                                <p className="text-sm text-[var(--muted)] mb-6">
                                    Authentication and access control settings.
                                </p>

                                <div className="space-y-6">
                                    <div className="p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]">
                                        <h3 className="font-medium mb-2">API Authentication</h3>
                                        <p className="text-sm text-[var(--muted)]">
                                            API endpoints are secured with JWT tokens. Configure API_SECRET_KEY in environment.
                                        </p>
                                    </div>

                                    <div className="p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]">
                                        <h3 className="font-medium mb-2">Agent Audit Logging</h3>
                                        <p className="text-sm text-[var(--muted)]">
                                            All agent actions are logged to the agent_events table for audit purposes.
                                        </p>
                                    </div>

                                    <div className="p-4 rounded-lg bg-[var(--card-hover)] border border-[var(--border)]">
                                        <h3 className="font-medium mb-2">CORS Configuration</h3>
                                        <p className="text-sm text-[var(--muted)]">
                                            Configure allowed origins in CORS_ORIGINS environment variable.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Save Button */}
                        <div className="mt-8 pt-6 border-t border-[var(--border)] flex justify-end">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className={clsx(
                                    'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors',
                                    saved
                                        ? 'bg-green-500/20 text-green-400'
                                        : 'bg-gradient-primary text-white hover:opacity-90',
                                    saving && 'opacity-50 cursor-not-allowed'
                                )}
                            >
                                {saved ? (
                                    <>
                                        <CheckCircle className="w-4 h-4" />
                                        Saved
                                    </>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4" />
                                        {saving ? 'Saving...' : 'Save Changes'}
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
