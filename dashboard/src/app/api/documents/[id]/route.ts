import { NextRequest, NextResponse } from 'next/server';
import { readFile, unlink } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

const DATA_DIR = process.env.DATA_DIR || path.join(process.cwd(), 'data');
const PROCESSED_DIR = path.join(DATA_DIR, 'processed');
const ARTIFACTS_DIR = path.join(DATA_DIR, 'artifacts');
const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const docPath = path.join(PROCESSED_DIR, `${params.id}.json`);

        if (!existsSync(docPath)) {
            return NextResponse.json({ detail: 'Document not found' }, { status: 404 });
        }

        const content = await readFile(docPath, 'utf-8');
        return NextResponse.json(JSON.parse(content));

    } catch (error: any) {
        return NextResponse.json({ detail: error.message }, { status: 500 });
    }
}

export async function DELETE(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const docPath = path.join(PROCESSED_DIR, `${params.id}.json`);

        if (!existsSync(docPath)) {
            return NextResponse.json({ detail: 'Document not found' }, { status: 404 });
        }

        // Read document to get artifact IDs
        const content = await readFile(docPath, 'utf-8');
        const doc = JSON.parse(content);

        // Delete artifacts
        for (const artifactId of doc.artifacts || []) {
            const artifactPath = path.join(ARTIFACTS_DIR, `${artifactId}.json`);
            if (existsSync(artifactPath)) {
                await unlink(artifactPath);
            }
        }

        // Delete PDF
        const pdfPath = path.join(UPLOADS_DIR, `${params.id}.pdf`);
        if (existsSync(pdfPath)) {
            await unlink(pdfPath);
        }

        // Delete document info
        await unlink(docPath);

        return NextResponse.json({ success: true, message: 'Document deleted' });

    } catch (error: any) {
        return NextResponse.json({ detail: error.message }, { status: 500 });
    }
}
