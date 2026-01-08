import { NextRequest, NextResponse } from 'next/server';
import { readFile, readdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

const DATA_DIR = process.env.DATA_DIR || path.join(process.cwd(), 'data');
const PROCESSED_DIR = path.join(DATA_DIR, 'processed');
const ARTIFACTS_DIR = path.join(DATA_DIR, 'artifacts');

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const docPath = path.join(PROCESSED_DIR, `${params.id}.json`);

        if (!existsSync(docPath)) {
            return NextResponse.json({ detail: 'Document not found' }, { status: 404 });
        }

        const docContent = await readFile(docPath, 'utf-8');
        const doc = JSON.parse(docContent);

        const artifacts = [];
        for (const artifactId of doc.artifacts || []) {
            const artifactPath = path.join(ARTIFACTS_DIR, `${artifactId}.json`);
            if (existsSync(artifactPath)) {
                const content = await readFile(artifactPath, 'utf-8');
                artifacts.push(JSON.parse(content));
            }
        }

        return NextResponse.json(artifacts);

    } catch (error: any) {
        return NextResponse.json({ detail: error.message }, { status: 500 });
    }
}
