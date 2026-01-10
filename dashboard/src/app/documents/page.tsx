'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
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
    ArrowUpDown,
    ExternalLink,
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
    review_pending_count: number;
    review_total_count: number;
    review_completed_count: number;
}

interface Artifact {
    id: string;
    document_id: string;
    artifact_type: string;
    title: string;
    content: string;
    created_at: string;
    review_status: string;
    reviewed_at: string | null;
    reviewed_by: string | null;
    review_notes: string | null;
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
    const [artifacts, setArtifacts] = useState<Artifact[]>([]);
    const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
    const [dragOver, setDragOver] = useState(false);
    const [docSort, setDocSort] = useState('uploaded_at');
    const [docSortDir, setDocSortDir] = useState<'asc' | 'desc'>('desc');
    const [artifactSort, setArtifactSort] = useState('created_at');
    const [artifactSortDir, setArtifactSortDir] = useState<'asc' | 'desc'>('desc');
    const [showPdf, setShowPdf] = useState(false);
    const [reviewerName, setReviewerName] = useState('');
    const [reviewNotes, setReviewNotes] = useState('');
    const [reviewUpdating, setReviewUpdating] = useState(false);

    useEffect(() => {
        fetchDocuments();
    }, []);

    useEffect(() => {
        setReviewNotes(selectedArtifact?.review_notes || '');
        if (selectedArtifact?.reviewed_by && !reviewerName) {
            setReviewerName(selectedArtifact.reviewed_by);
        }
    }, [selectedArtifact, reviewerName]);

    const fetchDocuments = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/documents/');
            if (res.ok) {
                const data = await res.json();
                setDocuments(data);
                return data as Document[];
            }
        } catch (error) {
            console.error('Failed to fetch documents:', error);
        } finally {
            setLoading(false);
        }
        return null;
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

            if (!res.ok) {
                const error = await res.json().catch(() => null);
                const detail = error?.detail || 'Upload failed';
                alert(`Upload failed: ${detail}`);
            }
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Upload failed - check console for details');
        } finally {
            setUploading(false);
            await fetchDocuments();
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
        setSelectedArtifact(null);
        setArtifacts([]);
        setShowPdf(false);
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

    const getReviewStatusColor = (status: string) => {
        switch (status) {
            case 'reviewed':
                return 'bg-green-500/20 text-green-400';
            case 'needs_revision':
                return 'bg-red-500/20 text-red-400';
            default:
                return 'bg-yellow-500/20 text-yellow-400';
        }
    };

    const sortedDocuments = useMemo(() => {
        const docs = [...documents];
        const direction = docSortDir === 'asc' ? 1 : -1;
        docs.sort((a, b) => {
            switch (docSort) {
                case 'filename':
                    return a.filename.localeCompare(b.filename) * direction;
                case 'status':
                    return a.status.localeCompare(b.status) * direction;
                case 'review_pending':
                    return (a.review_pending_count - b.review_pending_count) * direction;
                case 'uploaded_at':
                default:
                    return (new Date(a.uploaded_at).getTime() - new Date(b.uploaded_at).getTime()) * direction;
            }
        });
        return docs;
    }, [documents, docSort, docSortDir]);

    const sortedArtifacts = useMemo(() => {
        const items = [...artifacts];
        const direction = artifactSortDir === 'asc' ? 1 : -1;
        const reviewOrder: Record<string, number> = {
            pending_review: 0,
            needs_revision: 1,
            reviewed: 2,
        };
        items.sort((a, b) => {
            switch (artifactSort) {
                case 'artifact_type':
                    return a.artifact_type.localeCompare(b.artifact_type) * direction;
                case 'title':
                    return a.title.localeCompare(b.title) * direction;
                case 'review_status':
                    return ((reviewOrder[a.review_status] ?? 99) - (reviewOrder[b.review_status] ?? 99)) * direction;
                case 'created_at':
                default:
                    return (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) * direction;
            }
        });
        return items;
    }, [artifacts, artifactSort, artifactSortDir]);

    const updateArtifactReview = async (status: string) => {
        if (!selectedArtifact) return;
        const reviewer = reviewerName.trim();
        if (!reviewer) {
            alert('Reviewer name is required');
            return;
        }
        const notes = reviewNotes.trim();
        if (status === 'needs_revision' && !notes) {
            alert('Review notes are required when requesting revisions');
            return;
        }

        setReviewUpdating(true);
        try {
            const res = await fetch(`/api/documents/artifacts/${selectedArtifact.id}/review`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    review_status: status,
                    reviewed_by: reviewer,
                    review_notes: notes || null,
                }),
            });

            if (!res.ok) {
                const error = await res.json().catch(() => null);
                const detail = error?.detail || 'Failed to update review status';
                alert(detail);
                return;
            }

            const updated = await res.json();
            setArtifacts((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
            setSelectedArtifact(updated);
            const refreshed = await fetchDocuments();
            if (selectedDoc && refreshed) {
                const updatedDoc = refreshed.find((doc) => doc.id === selectedDoc.id);
                if (updatedDoc) {
                    setSelectedDoc(updatedDoc);
                }
            }
        } catch (error) {
            console.error('Failed to update review:', error);
            alert('Failed to update review status');
        } finally {
            setReviewUpdating(false);
        }
    };

    const pdfUrl = selectedDoc ? `/api/documents/${selectedDoc.id}/file` : '';
    const pageCount = selectedDoc?.page_count ?? 'Unknown';
    const textLength = selectedDoc?.text_length ? selectedDoc.text_length.toLocaleString() : 'Unknown';

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
                                    PDF files only. Analysis runs locally with no API keys.
                                </p>
                            </div>
                        </div>
                    )}
                </div>

<div className="grid grid-cols-3 gap-6">
    <div className="col-span-1 space-y-4">
        <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Uploaded Documents</h2>
            <div className="flex items-center gap-2">
                <select
                    value={docSort}
                    onChange={(e) => setDocSort(e.target.value)}
                    className="bg-[var(--card)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs"
                >
                    <option value="uploaded_at">Upload time</option>
                    <option value="filename">Filename</option>
                    <option value="status">Status</option>
                    <option value="review_pending">Review needed</option>
                </select>
                <button
                    onClick={() => setDocSortDir(docSortDir === 'asc' ? 'desc' : 'asc')}
                    className="p-1 rounded border border-[var(--border)] text-[var(--muted)] hover:text-white"
                    title="Toggle sort direction"
                >
                    <ArrowUpDown className="w-4 h-4" />
                </button>
            </div>
        </div>

        {loading ? (
            <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
        ) : sortedDocuments.length === 0 ? (
            <div className="text-center py-12 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                <FileText className="w-12 h-12 mx-auto mb-4 text-[var(--muted)] opacity-50" />
                <p className="text-[var(--muted)]">No documents yet</p>
                <p className="text-sm text-[var(--muted)]">Upload a PDF to get started</p>
            </div>
        ) : (
            sortedDocuments.map((doc) => (
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
                            {doc.review_total_count > 0 && (
                                <p className="text-xs text-[var(--muted)] mt-1">
                                    Review: {doc.review_completed_count}/{doc.review_total_count}
                                </p>
                            )}
                            {doc.review_pending_count > 0 && (
                                <p className="text-xs text-yellow-400 mt-1">
                                    {doc.review_pending_count} pending review
                                </p>
                            )}
                            {doc.status === 'error' && doc.error && (
                                <p className="text-xs text-red-400 mt-1 line-clamp-2">
                                    {doc.error}
                                </p>
                            )}
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

    <div className="col-span-2">
        {selectedDoc ? (
            <div>
                <div className="flex flex-col gap-3 mb-4">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div>
                            <h2 className="text-lg font-semibold">
                                Generated Artifacts ({artifacts.length})
                            </h2>
                            <p className="text-sm text-[var(--muted)] mt-1">
                                {pageCount} pages | {textLength} chars
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setShowPdf(!showPdf)}
                                className="px-3 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-sm hover:bg-[var(--card-hover)]"
                            >
                                {showPdf ? 'Hide PDF' : 'Preview PDF'}
                            </button>
                            <a
                                href={pdfUrl}
                                target="_blank"
                                rel="noreferrer"
                                className="px-3 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-sm hover:bg-[var(--card-hover)] inline-flex items-center gap-2"
                            >
                                <ExternalLink className="w-4 h-4" />
                                Open PDF
                            </a>
                            <a
                                href={pdfUrl}
                                download
                                className="px-3 py-2 rounded-lg bg-[var(--card)] border border-[var(--border)] text-sm hover:bg-[var(--card-hover)] inline-flex items-center gap-2"
                            >
                                <Download className="w-4 h-4" />
                                Download
                            </a>
                        </div>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-[var(--muted)]">
                            {selectedDoc.review_pending_count > 0
                                ? `${selectedDoc.review_pending_count} artifacts need review`
                                : 'No pending reviews'}
                        </span>
                        <div className="flex items-center gap-2">
                            <select
                                value={artifactSort}
                                onChange={(e) => setArtifactSort(e.target.value)}
                                className="bg-[var(--card)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs"
                            >
                                <option value="created_at">Created</option>
                                <option value="artifact_type">Type</option>
                                <option value="title">Title</option>
                                <option value="review_status">Review status</option>
                            </select>
                            <button
                                onClick={() => setArtifactSortDir(artifactSortDir === 'asc' ? 'desc' : 'asc')}
                                className="p-1 rounded border border-[var(--border)] text-[var(--muted)] hover:text-white"
                                title="Toggle sort direction"
                            >
                                <ArrowUpDown className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>

                {showPdf && (
                    <div className="mb-6 bg-[var(--card)] border border-[var(--border)] rounded-xl p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-semibold">PDF Preview</h3>
                            <button
                                onClick={() => setShowPdf(false)}
                                className="p-1 rounded hover:bg-[var(--card-hover)]"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                        <iframe
                            src={pdfUrl}
                            title="PDF Preview"
                            className="w-full h-[520px] rounded-lg border border-[var(--border)]"
                        />
                    </div>
                )}

                {selectedDoc.status === 'error' ? (
                    <div className="text-center py-12 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                        <AlertCircle className="w-8 h-8 mx-auto mb-4 text-red-400" />
                        <p className="text-[var(--muted)]">Processing failed.</p>
                        {selectedDoc.error && (
                            <p className="text-xs text-red-400 mt-2">{selectedDoc.error}</p>
                        )}
                    </div>
                ) : selectedDoc.status === 'processing' ? (
                    <div className="text-center py-12 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                        <Loader2 className="w-8 h-8 mx-auto mb-4 animate-spin text-blue-400" />
                        <p className="text-[var(--muted)]">Processing...</p>
                    </div>
                ) : sortedArtifacts.length === 0 ? (
                    <div className="text-center py-12 bg-[var(--card)] rounded-xl border border-[var(--border)]">
                        <FileText className="w-8 h-8 mx-auto mb-4 text-[var(--muted)]" />
                        <p className="text-[var(--muted)]">No artifacts available.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-4 mb-6">
                        {sortedArtifacts.map((artifact) => (
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
                                    <span
                                        className={clsx(
                                            'px-2 py-0.5 rounded text-xs font-medium capitalize',
                                            getReviewStatusColor(artifact.review_status)
                                        )}
                                    >
                                        {artifact.review_status.replace('_', ' ')}
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
                        <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                            <div>
                                <h3 className="text-xl font-semibold">{selectedArtifact.title}</h3>
                                <div className="flex flex-wrap items-center gap-2 mt-2">
                                    <span
                                        className={clsx(
                                            'px-2 py-0.5 rounded text-xs font-medium capitalize',
                                            getArtifactTypeColor(selectedArtifact.artifact_type)
                                        )}
                                    >
                                        {selectedArtifact.artifact_type.replace('_', ' ')}
                                    </span>
                                    <span
                                        className={clsx(
                                            'px-2 py-0.5 rounded text-xs font-medium capitalize',
                                            getReviewStatusColor(selectedArtifact.review_status)
                                        )}
                                    >
                                        {selectedArtifact.review_status.replace('_', ' ')}
                                    </span>
                                    {selectedArtifact.reviewed_by && (
                                        <span className="text-xs text-[var(--muted)]">
                                            Reviewed by {selectedArtifact.reviewed_by}
                                        </span>
                                    )}
                                    {selectedArtifact.reviewed_at && (
                                        <span className="text-xs text-[var(--muted)]">
                                            {formatDistanceToNow(new Date(selectedArtifact.reviewed_at), { addSuffix: true })}
                                        </span>
                                    )}
                                </div>
                            </div>
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

                        <div className="mt-6 border-t border-[var(--border)] pt-4">
                            <h4 className="text-sm font-semibold mb-3">Review</h4>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs text-[var(--muted)]">Reviewer Name</label>
                                    <input
                                        value={reviewerName}
                                        onChange={(e) => setReviewerName(e.target.value)}
                                        className="mt-2 w-full rounded-lg bg-[var(--card-hover)] border border-[var(--border)] px-3 py-2 text-sm"
                                        placeholder="Enter your name"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-[var(--muted)]">Current Status</label>
                                    <div className="mt-2">
                                        <span
                                            className={clsx(
                                                'px-2 py-1 rounded text-xs font-medium capitalize',
                                                getReviewStatusColor(selectedArtifact.review_status)
                                            )}
                                        >
                                            {selectedArtifact.review_status.replace('_', ' ')}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-4">
                                <label className="text-xs text-[var(--muted)]">Review Notes</label>
                                <textarea
                                    value={reviewNotes}
                                    onChange={(e) => setReviewNotes(e.target.value)}
                                    rows={4}
                                    className="mt-2 w-full rounded-lg bg-[var(--card-hover)] border border-[var(--border)] px-3 py-2 text-sm"
                                    placeholder="Summarize issues, requests, or approval rationale"
                                />
                            </div>
                            <div className="mt-4 flex flex-wrap gap-2">
                                <button
                                    onClick={() => updateArtifactReview('reviewed')}
                                    disabled={reviewUpdating}
                                    className="px-4 py-2 rounded-lg bg-green-500/20 text-green-200 text-sm font-medium hover:bg-green-500/30 disabled:opacity-50"
                                >
                                    {reviewUpdating ? 'Updating...' : 'Mark Reviewed'}
                                </button>
                                <button
                                    onClick={() => updateArtifactReview('needs_revision')}
                                    disabled={reviewUpdating}
                                    className="px-4 py-2 rounded-lg bg-red-500/20 text-red-200 text-sm font-medium hover:bg-red-500/30 disabled:opacity-50"
                                >
                                    Request Revision
                                </button>
                                <button
                                    onClick={() => updateArtifactReview('pending_review')}
                                    disabled={reviewUpdating}
                                    className="px-4 py-2 rounded-lg bg-[var(--card-hover)] text-[var(--muted)] text-sm font-medium hover:text-white disabled:opacity-50"
                                >
                                    Reset to Pending
                                </button>
                            </div>
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
