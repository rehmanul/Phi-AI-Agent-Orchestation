import { NextRequest, NextResponse } from 'next/server';
import { readdir, readFile } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

const DATA_DIR = process.env.DATA_DIR || path.join(process.cwd(), 'data');
const PROCESSED_DIR = path.join(DATA_DIR, 'processed');

export async function GET() {
    try {
        if (!existsSync(PROCESSED_DIR)) {
            return NextResponse.json([]);
        }

        const files = await readdir(PROCESSED_DIR);
        const documents = [];

        for (const file of files) {
            if (file.endsWith('.json')) {
                const content = await readFile(path.join(PROCESSED_DIR, file), 'utf-8');
                documents.push(JSON.parse(content));
            }
        }

        // Sort by upload date (newest first)
        documents.sort((a, b) =>
            new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime()
        );

        return NextResponse.json(documents);

    } catch (error: any) {
        console.error('List documents error:', error);
        return NextResponse.json([], { status: 200 });
    }
}
