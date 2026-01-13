import { NextRequest } from 'next/server';
import { buildBackendUrl, proxyJsonResponse } from '../../proxy';

export const dynamic = 'force-dynamic';

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const res = await fetch(
            buildBackendUrl(`/api/documents/${params.id}/artifacts`, request),
            { cache: 'no-store' }
        );
        return proxyJsonResponse(res, []);
    } catch (error: unknown) {
        console.error('Get artifacts error:', error);
        return proxyJsonResponse(null, []);
    }
}
