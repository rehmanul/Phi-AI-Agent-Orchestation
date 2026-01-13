import { NextRequest } from 'next/server';
import { buildBackendUrl, proxyJsonResponse } from '../proxy';

export const dynamic = 'force-dynamic';

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const res = await fetch(buildBackendUrl(`/api/documents/${params.id}`, request), {
            cache: 'no-store',
        });
        return proxyJsonResponse(res, { detail: 'Document not found' });
    } catch (error: unknown) {
        console.error('Get document error:', error);
        return proxyJsonResponse(null, { detail: 'Document not found' });
    }
}

export async function DELETE(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const res = await fetch(buildBackendUrl(`/api/documents/${params.id}`, request), {
            method: 'DELETE',
            cache: 'no-store',
        });
        return proxyJsonResponse(res, { detail: 'Delete failed' });
    } catch (error: unknown) {
        console.error('Delete document error:', error);
        return proxyJsonResponse(null, { detail: 'Delete failed' });
    }
}
