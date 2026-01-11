import { NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://localhost:8000';

export async function GET() {
    try {
        const res = await fetch(`${API_URL}/api/documents/`, { cache: 'no-store' });
        if (!res.ok) {
            return NextResponse.json([], { status: res.status });
        }

        const documents = await res.json();
        return NextResponse.json(documents);
    } catch (error: unknown) {
        console.error('List documents error:', error);
        return NextResponse.json([], { status: 200 });
    }
}
