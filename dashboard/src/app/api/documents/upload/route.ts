import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir, readFile } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// Use PDFParser for server-side text extraction
// For now, we'll do basic processing without external dependencies

const DATA_DIR = process.env.DATA_DIR || path.join(process.cwd(), 'data');
const UPLOADS_DIR = path.join(DATA_DIR, 'uploads');
const PROCESSED_DIR = path.join(DATA_DIR, 'processed');
const ARTIFACTS_DIR = path.join(DATA_DIR, 'artifacts');

async function ensureDirs() {
    for (const dir of [UPLOADS_DIR, PROCESSED_DIR, ARTIFACTS_DIR]) {
        if (!existsSync(dir)) {
            await mkdir(dir, { recursive: true });
        }
    }
}

function generateSummary(filename: string): string {
    return `## Document Summary

### File Information
- **Filename**: ${filename}
- **Uploaded**: ${new Date().toISOString()}

### Content Analysis
This document has been uploaded and is ready for processing.

When LLM API keys are configured, this will provide:
- Detailed content summary
- Key entity extraction
- Legislative action items
- Stakeholder analysis

---
*Processing completed at ${new Date().toLocaleString()}*`;
}

function generateEntities(filename: string): string {
    return `## Extracted Entities

### Document
- **Source File**: ${filename}

### Entities
Detailed entity extraction requires LLM processing. Configure API keys in Settings to enable:
- Organization identification
- Legal reference parsing
- Monetary value detection
- Date extraction
- Key term identification

---
*Configure OpenAI or Anthropic API key to enable full entity extraction.*`;
}

function generateActionPlan(filename: string): string {
    return `## Recommended Actions

Based on document upload, recommended next steps:

1. **Review Document Content**
   - Open the original PDF for manual review
   - Identify key sections relevant to wireless power policy

2. **Configure API Keys**
   - Go to Settings → Add OpenAI or Anthropic API key
   - Enable full AI-powered analysis

3. **Process with AI**
   - Re-upload document after configuring API keys
   - Receive detailed analysis and recommendations

4. **Share with Team**
   - Export artifacts for stakeholder review
   - Schedule strategy session

---
*Full action plan generation requires LLM API keys.*`;
}

export async function POST(request: NextRequest) {
    try {
        await ensureDirs();

        const formData = await request.formData();
        const file = formData.get('file') as File;

        if (!file) {
            return NextResponse.json({ detail: 'No file provided' }, { status: 400 });
        }

        if (!file.name.toLowerCase().endsWith('.pdf')) {
            return NextResponse.json({ detail: 'Only PDF files are supported' }, { status: 400 });
        }

        // Generate document ID
        const docId = uuidv4();

        // Save uploaded file
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);
        const filePath = path.join(UPLOADS_DIR, `${docId}.pdf`);
        await writeFile(filePath, buffer);

        // Create artifacts (without LLM for now)
        const artifacts = [];

        // Summary artifact
        const summaryArtifact = {
            id: uuidv4(),
            document_id: docId,
            artifact_type: 'summary',
            title: 'Document Summary',
            content: generateSummary(file.name),
            created_at: new Date().toISOString(),
        };
        artifacts.push(summaryArtifact);
        await writeFile(
            path.join(ARTIFACTS_DIR, `${summaryArtifact.id}.json`),
            JSON.stringify(summaryArtifact, null, 2)
        );

        // Entities artifact
        const entitiesArtifact = {
            id: uuidv4(),
            document_id: docId,
            artifact_type: 'entities',
            title: 'Key Entities & Terms',
            content: generateEntities(file.name),
            created_at: new Date().toISOString(),
        };
        artifacts.push(entitiesArtifact);
        await writeFile(
            path.join(ARTIFACTS_DIR, `${entitiesArtifact.id}.json`),
            JSON.stringify(entitiesArtifact, null, 2)
        );

        // Action plan artifact
        const actionArtifact = {
            id: uuidv4(),
            document_id: docId,
            artifact_type: 'action_plan',
            title: 'Recommended Actions',
            content: generateActionPlan(file.name),
            created_at: new Date().toISOString(),
        };
        artifacts.push(actionArtifact);
        await writeFile(
            path.join(ARTIFACTS_DIR, `${actionArtifact.id}.json`),
            JSON.stringify(actionArtifact, null, 2)
        );

        // Create document info
        const docInfo = {
            id: docId,
            filename: file.name,
            status: 'completed',
            page_count: null,
            text_length: null,
            uploaded_at: new Date().toISOString(),
            processed_at: new Date().toISOString(),
            artifacts: artifacts.map(a => a.id),
            error: null,
        };

        await writeFile(
            path.join(PROCESSED_DIR, `${docId}.json`),
            JSON.stringify(docInfo, null, 2)
        );

        return NextResponse.json(docInfo);

    } catch (error: any) {
        console.error('Upload error:', error);
        return NextResponse.json(
            { detail: `Upload failed: ${error.message}` },
            { status: 500 }
        );
    }
}
