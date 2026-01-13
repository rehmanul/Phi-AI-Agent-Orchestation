import { NextRequest } from 'next/server';
import { buildBackendUrl, proxyJsonResponse } from '../proxy';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const res = await fetch(buildBackendUrl('/api/documents/upload'), {
            method: 'POST',
            body: formData,
            cache: 'no-store',
        });
        return proxyJsonResponse(res, { detail: 'Upload failed' });
    } catch (error: unknown) {
        console.error('Upload error:', error);
        return proxyJsonResponse(null, { detail: 'Upload failed' });
    }
}
