import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const API_URL = process.env.API_URL || 'http://localhost:8000';

export const buildBackendUrl = (path: string, request?: NextRequest) => {
    const search = request?.nextUrl.search ?? '';
    return `${API_URL}${path}${search}`;
};

export const proxyJsonResponse = async <T>(res: Response | null, fallback: T) => {
    if (!res) {
        return NextResponse.json(fallback, { status: 200 });
    }

    const contentType = res.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        const data = await res.json();
        return NextResponse.json(data, { status: res.status });
    }

    const text = await res.text();
    return new NextResponse(text, {
        status: res.status,
        headers: {
            'content-type': contentType || 'application/json',
        },
    });
};
