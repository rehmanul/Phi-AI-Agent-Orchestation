'use client';

import { useState, useEffect, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import {
    Upload,
    FileText,
    CheckCircle,
    AlertCircle,
    Loader2,
    Trash2,
    Eye,
    X,
    FileType,
    Clock,
    Download,
} from 'lucide-react';

interface Document {
    id: string;
    filename: string;
    status: string;
    page_count: number | null;
    text_length: number | null;
    uploaded_at: string;
    processed_at: string | null;
    artifacts: string[];
    error: string | null;
}

interface Artifact {
    id: string;
    document_id: string;
    artifact_type: string;
    title: string;
    content: string;
    created_at: string;
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
    const [artifacts, setArtifacts] = useState<Artifact[]>([]);
    const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
    const [dragOver, setDragOver] = useState(false);

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            const res = await fetch('/api/documents/');
            if (res.ok) {
                const data = await res.json();
                setDocuments(data);
            }
        } catch (error) {
            console.error('Failed to fetch documents:', error);
        } finally {
            setLoading(false);
        }
    };

    const uploadFile = async (file: File) => {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('Only PDF files are supported');
            return;
        }

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData,
            });

            if (res.ok) {
                await fetchDocuments();
            } else {
                const error = await res.json();
                alert(`Upload failed: ${error.detail}`);
            }
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Upload failed - check console for details');
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }, []);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            uploadFile(files[0]);
        }
    };

    const viewDocument = async (doc: Document) => {
        setSelectedDoc(doc);
        try {
            const res = await fetch(`/api/documents/${doc.id}/artifacts`);
            if (res.ok) {
                const data = await res.json();
                setArtifacts(data);
            }
        } catch (error) {
            console.error('Failed to fetch artifacts:', error);
        }
    };

    const deleteDocument = async (docId: string) => {
        if (!confirm('Delete this document and all its artifacts?')) return;

        try {
            await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
            setDocuments(documents.filter(d => d.id !== docId));
            if (selectedDoc?.id === docId) {
                setSelectedDoc(null);
                setArtifacts([]);
            }
        } catch (error) {
            console.error('Failed to delete document:', error);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-5 h-5 text-green-400" />;
            case 'processing':
                return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-400" />;
            default:
                return <Clock className="w-5 h-5 text-yellow-400" />;
        }
    };

    const getArtifactTypeColor = (type: string) => {
        switch (type) {
            case 'summary':
                return 'bg-blue-500/20 text-blue-400';
            case 'entities':
                return 'bg-green-500/20 text-green-400';
            case 'action_plan':
                return 'bg-purple-500/20 text-purple-400';
            case 'full_text':
                return 'bg-gray-500/20 text-gray-400';
            default:
                return 'bg-yellow-500/20 text-yellow-400';
        }
    };

    return (
        <div className="flex min-h-screen bg-[var(--background)]">
            <Sidebar />

            <main className="flex-1 p-8 ml-64">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold">Documents</h1>
                    <p className="text-[var(--muted)] mt-2">
                        Upload PDFs to process and view generated artifacts
                    </p>
                </header>

                {/* Upload Zone */}
                <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    className={clsx(
                        'border-2 border-dashed rounded-xl p-8 mb-8 text-center transition-colors',
                        dragOver
                            ? 'border-blue-500 bg-blue-500/10'
                            : 'border-[var(--border)] hover:border-blue-500/50'
                    )}
                >
                    {uploading ? (
                        <div className="flex flex-col items-center gap-4">
                            <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
                            <p className="text-lg">Processing document...</p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-4">
                            <Upload className="w-12 h-12 text-[var(--muted)]" />
                            <div>
                                <p className="text-lg mb-2">
                                    Drag and drop a PDF here, or{' '}
                                    <label className="text-blue-400 cursor-pointer hover:underline">
                                        browse
                                        <input
                                            type="file"
                                            accept=".pdf"
                                            onChange={handleFileSelect}
                                            className="hidden"
                                        />
                                    </label>
                                </p>
                                <p className="text-sm text-[var(--muted)]">
                                    PDF files only • No API keys required
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                <div className="grid grid-cols-3 gap-6">
                    {/* Documents List */}
                    <div className="col-span-1 space-y-4">
                        <h2 className="text-lg font-semibold mb-4">Uploaded Documents</h2>

                        {loading ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                            </div>
                        ) : documents.length === 0 ? (
                            <div className="text-center py-12 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                                <FileText className="w-12 h-12 mx-auto mb-4 text-[var(--muted)] opacity-50" />
                                <p className="text-[var(--muted)]">No documents yet</p>
                                <p className="text-sm text-[var(--muted)]">Upload a PDF to get started</p>
                            </div>
                        ) : (
                            documents.map((doc) => (
                                <div
                                    key={doc.id}
                                    onClick={() => viewDocument(doc)}
                                    className={clsx(
                                        'p-4 rounded-xl bg-[var(--card)] border cursor-pointer transition-colors',
                                        selectedDoc?.id === doc.id
                                            ? 'border-blue-500'
                                            : 'border-[var(--border)] hover:border-blue-500/50'
                                    )}
                                >
                                    <div className="flex items-start gap-3">
                                        <FileType className="w-8 h-8 text-red-400 flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium truncate">{doc.filename}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                {getStatusIcon(doc.status)}
                                                <span className="text-xs text-[var(--muted)] capitalize">
                                                    {doc.status}
                                                </span>
                                            </div>
                                            <p className="text-xs text-[var(--muted)] mt-1">
                                                {formatDistanceToNow(new Date(doc.uploaded_at), { addSuffix: true })}
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                deleteDocument(doc.id);
                                            }}
                                            className="p-1 rounded hover:bg-red-500/20 text-[var(--muted)] hover:text-red-400"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Artifacts View */}
                    <div className="col-span-2">
                        {selectedDoc ? (
                            <div>
                                <div className="flex items-center justify-between mb-4">
                                    <h2 className="text-lg font-semibold">
                                        Generated Artifacts ({artifacts.length})
                                    </h2>
                                    <div className="text-sm text-[var(--muted)]">
                                        {selectedDoc.page_count} pages • {selectedDoc.text_length?.toLocaleString()} chars
                                    </div>
                                </div>

                                {artifacts.length === 0 ? (
                                    <div className="text-center py-12 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                                        <Loader2 className="w-8 h-8 mx-auto mb-4 animate-spin text-blue-400" />
                                        <p className="text-[var(--muted)]">Processing...</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        {artifacts.map((artifact) => (
                                            <div
                                                key={artifact.id}
                                                onClick={() => setSelectedArtifact(artifact)}
                                                className={clsx(
                                                    'p-4 rounded-xl bg-[var(--card)] border cursor-pointer transition-colors',
                                                    selectedArtifact?.id === artifact.id
                                                        ? 'border-blue-500'
                                                        : 'border-[var(--border)] hover:border-blue-500/50'
                                                )}
                                            >
                                                <div className="flex items-center gap-2 mb-2">
                                                    <span
                                                        className={clsx(
                                                            'px-2 py-0.5 rounded text-xs font-medium capitalize',
                                                            getArtifactTypeColor(artifact.artifact_type)
                                                        )}
                                                    >
                                                        {artifact.artifact_type.replace('_', ' ')}
                                                    </span>
                                                </div>
                                                <p className="font-medium">{artifact.title}</p>
                                                <p className="text-xs text-[var(--muted)] mt-1 line-clamp-2">
                                                    {artifact.content.slice(0, 100)}...
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Artifact Content Viewer */}
                                {selectedArtifact && (
                                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <h3 className="text-xl font-semibold">{selectedArtifact.title}</h3>
                                            <button
                                                onClick={() => setSelectedArtifact(null)}
                                                className="p-1 rounded hover:bg-[var(--card-hover)]"
                                            >
                                                <X className="w-5 h-5" />
                                            </button>
                                        </div>
                                        <div className="prose prose-invert max-w-none">
                                            <pre className="whitespace-pre-wrap text-sm font-sans bg-[var(--card-hover)] p-4 rounded-lg overflow-auto max-h-[500px]">
                                                {selectedArtifact.content}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-20 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                                <Eye className="w-12 h-12 mx-auto mb-4 text-[var(--muted)] opacity-50" />
                                <p className="text-lg text-[var(--muted)]">Select a document to view artifacts</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
