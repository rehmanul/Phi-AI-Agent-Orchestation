'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import {
    FileCode,
    RefreshCw,
    Loader2,
    ChevronDown,
    Download,
    ZoomIn,
    ZoomOut,
    Maximize2,
} from 'lucide-react';

// Declare mermaid on window
declare global {
    interface Window {
        mermaid: {
            initialize: (config: object) => void;
            render: (id: string, content: string) => Promise<{ svg: string }>;
        };
    }
}

interface DiagramInfo {
    name: string;
    filename: string;
    path: string;
    size_bytes: number;
}

export default function DiagramsPage() {
    const [diagrams, setDiagrams] = useState<DiagramInfo[]>([]);
    const [selectedDiagram, setSelectedDiagram] = useState<string | null>(null);
    const [diagramContent, setDiagramContent] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [rendering, setRendering] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const diagramRef = useRef<HTMLDivElement>(null);

    const fetchDiagrams = useCallback(async () => {
        try {
            const res = await fetch('/api/diagrams/');
            if (res.ok) {
                const data = await res.json();
                setDiagrams(data.diagrams);
            }
        } catch (error) {
            console.error('Failed to fetch diagrams:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    const loadDiagram = async (filename: string) => {
        setSelectedDiagram(filename);
        setRendering(true);
        setError(null);

        try {
            const res = await fetch(`/api/diagrams/${encodeURIComponent(filename)}`);
            if (res.ok) {
                const data = await res.json();
                setDiagramContent(data.content);
            } else {
                setError('Failed to load diagram');
            }
        } catch (error) {
            setError('Error loading diagram');
        } finally {
            setRendering(false);
        }
    };

    useEffect(() => {
        fetchDiagrams();
    }, [fetchDiagrams]);

    // Render mermaid when content changes
    useEffect(() => {
        if (!diagramContent || !diagramRef.current) return;

        const renderMermaid = async () => {
            try {
                // @ts-ignore - Mermaid is loaded dynamically
                if (typeof window !== 'undefined' && window.mermaid) {
                    diagramRef.current!.innerHTML = '';
                    const { svg } = await window.mermaid.render('diagram', diagramContent);
                    diagramRef.current!.innerHTML = svg;
                } else {
                    // Show raw code if mermaid not loaded
                    diagramRef.current!.innerHTML = `<pre style="white-space: pre-wrap; font-size: 12px; padding: 20px;">${diagramContent}</pre>`;
                }
            } catch (error) {
                console.error('Mermaid render error:', error);
                // Show raw code on error
                diagramRef.current!.innerHTML = `<div style="padding: 20px;"><p style="color: #f87171; margin-bottom: 10px;">Diagram too complex for browser rendering</p><pre style="white-space: pre-wrap; font-size: 11px; max-height: 500px; overflow: auto;">${diagramContent}</pre></div>`;
            }
        };

        renderMermaid();
    }, [diagramContent]);

    // Load mermaid dynamically
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
        script.onload = () => {
            // @ts-ignore
            window.mermaid.initialize({
                startOnLoad: false,
                theme: 'dark',
                securityLevel: 'loose',
                maxTextSize: 100000,
            });
        };
        document.head.appendChild(script);

        return () => {
            document.head.removeChild(script);
        };
    }, []);

    const downloadDiagram = () => {
        if (!diagramContent) return;
        const blob = new Blob([diagramContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = selectedDiagram || 'diagram.mmd';
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">System Diagrams</h1>
                        <p className="text-[var(--muted)] mt-2">
                            View Mermaid architecture diagrams • {diagrams.length} available
                        </p>
                    </div>
                    <button
                        onClick={fetchDiagrams}
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
                    <div className="grid grid-cols-4 gap-6">
                        {/* Diagram List */}
                        <div className="col-span-1 space-y-2">
                            <h2 className="text-sm font-semibold text-[var(--muted)] mb-3">Available Diagrams</h2>
                            {diagrams.length === 0 ? (
                                <p className="text-[var(--muted)] text-sm">No diagrams found</p>
                            ) : (
                                diagrams.map((diagram) => (
                                    <button
                                        key={diagram.filename}
                                        onClick={() => loadDiagram(diagram.filename)}
                                        className={clsx(
                                            'w-full p-3 rounded-lg text-left transition-colors',
                                            selectedDiagram === diagram.filename
                                                ? 'bg-blue-500/20 border border-blue-500'
                                                : 'bg-[var(--card)] border border-[var(--border)] hover:bg-[var(--card-hover)]'
                                        )}
                                    >
                                        <div className="flex items-center gap-2">
                                            <FileCode className="w-4 h-4 text-purple-400" />
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-sm truncate">{diagram.name}</p>
                                                <p className="text-xs text-[var(--muted)]">
                                                    {(diagram.size_bytes / 1024).toFixed(1)} KB
                                                </p>
                                            </div>
                                        </div>
                                    </button>
                                ))
                            )}
                        </div>

                        {/* Diagram Viewer */}
                        <div className="col-span-3">
                            <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden">
                                {selectedDiagram ? (
                                    <>
                                        <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
                                            <h3 className="font-semibold">{selectedDiagram}</h3>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={downloadDiagram}
                                                    className="p-2 rounded-lg hover:bg-[var(--card-hover)]"
                                                    title="Download .mmd"
                                                >
                                                    <Download className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                        <div
                                            ref={diagramRef}
                                            className="p-4 min-h-[500px] max-h-[700px] overflow-auto bg-[#1a1a2e]"
                                        >
                                            {rendering && (
                                                <div className="flex items-center justify-center py-20">
                                                    <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                                                </div>
                                            )}
                                            {error && (
                                                <div className="text-center py-20 text-red-400">
                                                    {error}
                                                </div>
                                            )}
                                        </div>
                                    </>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-20 text-[var(--muted)]">
                                        <FileCode className="w-12 h-12 mb-4 opacity-50" />
                                        <p>Select a diagram to view</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
