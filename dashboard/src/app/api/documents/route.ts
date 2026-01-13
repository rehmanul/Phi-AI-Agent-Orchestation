import { NextRequest } from 'next/server';
import { buildBackendUrl, proxyJsonResponse } from './proxy';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    try {
        const res = await fetch(buildBackendUrl('/api/documents/', request), { cache: 'no-store' });
        return proxyJsonResponse(res, []);
    } catch (error: unknown) {
        console.error('List documents error:', error);
        return proxyJsonResponse(null, []);
    }
}
