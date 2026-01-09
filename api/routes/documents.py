"""
Document Processing API Routes

Provides endpoints for:
- PDF upload and text extraction
- Document processing pipeline
- Viewing generated artifacts
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import tiktoken
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.llm.client import LLMClient
from core.settings import get_setting_value

# PDF text extraction
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


router = APIRouter(prefix="/documents", tags=["documents"])

# Storage directories
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
UPLOADS_DIR = DATA_DIR / "uploads"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
PROCESSED_DIR = DATA_DIR / "processed"

# Ensure directories exist
for d in [UPLOADS_DIR, ARTIFACTS_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Pydantic Models
# =============================================================================

class DocumentInfo(BaseModel):
    id: str
    filename: str
    status: str  # uploaded, processing, completed, error
    page_count: Optional[int] = None
    text_length: Optional[int] = None
    uploaded_at: str
    processed_at: Optional[str] = None
    artifacts: List[str] = []
    error: Optional[str] = None
    review_pending_count: int = 0
    review_total_count: int = 0
    review_completed_count: int = 0


class ArtifactInfo(BaseModel):
    id: str
    document_id: str
    artifact_type: str  # analysis, summary, brief, action_plan, etc.
    title: str
    content: str
    created_at: str
    review_status: str = "pending_review"
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class ProcessingResult(BaseModel):
    document_id: str
    status: str
    message: str
    artifacts: List[str] = []


class ArtifactReviewUpdate(BaseModel):
    review_status: str
    reviewed_by: str
    review_notes: Optional[str] = None


# =============================================================================
# PDF Text Extraction
# =============================================================================

def extract_text_from_pdf(file_path: Path) -> tuple[str, int]:
    """
    Extract text from a PDF file.
    Returns (text, page_count).
    """
    text = ""
    page_count = 0
    
    # Try pdfplumber first (better quality)
    if HAS_PDFPLUMBER:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            if text.strip():
                return text.strip(), page_count
        except Exception:
            pass
    
    # Fallback to PyPDF2
    if HAS_PYPDF2:
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text.strip(), page_count
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")
    
    raise HTTPException(
        status_code=500, 
        detail="No PDF extraction library available. Install pdfplumber or PyPDF2."
    )


REVIEW_PENDING = "pending_review"
REVIEW_REVIEWED = "reviewed"
REVIEW_NEEDS_REVISION = "needs_revision"

CHUNK_TOKEN_LIMIT = 2500
CHUNK_OVERLAP = 200
ENTITY_TYPES = [
    "people",
    "organizations",
    "locations",
    "bills",
    "committees",
    "agencies",
    "regulations",
    "dates",
    "monetary_values",
]


def _get_llm_client() -> LLMClient:
    provider = (get_setting_value("llm_provider") or "openai").lower()
    if provider not in ("openai", "anthropic"):
        raise HTTPException(status_code=422, detail="Unsupported LLM provider")
    api_key = get_setting_value(f"{provider}_api_key")
    if not api_key:
        raise HTTPException(status_code=422, detail=f"{provider} API key is not configured")
    return LLMClient(provider=provider, api_key=api_key, temperature=0.2, max_tokens=2048)


def _get_tokenizer(model: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def _chunk_text(text: str, model: str, max_tokens: int = CHUNK_TOKEN_LIMIT) -> List[str]:
    if not text.strip():
        return []
    encoding = _get_tokenizer(model)
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return [text]
    step = max(1, max_tokens - CHUNK_OVERLAP)
    chunks = []
    for idx in range(0, len(tokens), step):
        chunk_tokens = tokens[idx: idx + max_tokens]
        if not chunk_tokens:
            continue
        chunks.append(encoding.decode(chunk_tokens))
    return chunks


async def _summarize_chunks(llm: LLMClient, chunks: List[str]) -> str:
    system_prompt = (
        "You are a senior policy analyst. Provide rigorous, factual summaries of "
        "legislative and regulatory documents. Avoid speculation."
    )
    if len(chunks) == 1:
        prompt = (
            "Summarize the document with clear headings and bullets. Include: "
            "Executive Summary, Key Findings, Stakeholders, Deadlines, "
            "Compliance Obligations, and Open Questions.\n\n"
            f"TEXT:\n{chunks[0]}"
        )
        return await llm.generate(prompt, system_prompt=system_prompt)

    section_summaries = []
    for idx, chunk in enumerate(chunks, 1):
        prompt = (
            f"Summarize section {idx} of {len(chunks)}. Capture concrete facts, "
            "definitions, deadlines, and obligations. Use bullets and short headings.\n\n"
            f"TEXT:\n{chunk}"
        )
        section_summaries.append(await llm.generate(prompt, system_prompt=system_prompt))

    combined_prompt = (
        "Combine the section summaries into a cohesive document summary with these "
        "sections: Executive Summary, Key Findings, Stakeholders and Agencies, "
        "Deadlines and Dates, Compliance Requirements, Risks or Conflicts, and "
        "Open Questions. Keep it concise but complete.\n\nSECTION SUMMARIES:\n"
        + "\n\n".join(section_summaries)
    )
    return await llm.generate(combined_prompt, system_prompt=system_prompt)


async def _extract_entities(llm: LLMClient, chunks: List[str]) -> Dict[str, List[str]]:
    results = await asyncio.gather(
        *[llm.extract_entities(chunk, entity_types=ENTITY_TYPES) for chunk in chunks]
    )
    merged: Dict[str, set] = {}
    for result in results:
        for key, values in result.items():
            if key not in merged:
                merged[key] = set()
            merged[key].update(v.strip() for v in values if v.strip())
    return {key: sorted(list(values)) for key, values in merged.items()}


def _format_entities(entities: Dict[str, List[str]]) -> str:
    if not entities:
        return "## Extracted Entities\n\nNo entities detected."
    output = "## Extracted Entities\n\n"
    for key in sorted(entities.keys()):
        items = entities[key]
        if not items:
            continue
        heading = key.replace("_", " ").title()
        output += f"### {heading}\n"
        for item in items:
            output += f"- {item}\n"
        output += "\n"
    return output.strip()


async def _generate_action_plan(
    llm: LLMClient,
    summary: str,
    entities: Dict[str, List[str]],
) -> str:
    entities_preview = json.dumps(entities, indent=2)
    system_prompt = (
        "You are a policy operations lead. Produce concrete, actionable plans "
        "grounded in the source document."
    )
    prompt = (
        "Create an action plan based on the document summary and extracted entities. "
        "Include sections: Immediate Actions (0-30 days), Mid-Term Actions (30-90 days), "
        "Stakeholder Engagement, Legal/Compliance Steps, Communications Plan, and Risks "
        "with Mitigations. Use numbered tasks with clear intent.\n\n"
        f"SUMMARY:\n{summary}\n\nENTITIES:\n{entities_preview}"
    )
    return await llm.generate(prompt, system_prompt=system_prompt)


async def process_document(doc_id: str, text: str) -> List[dict]:
    """
    Process extracted text and generate artifacts using the configured LLM provider.
    """
    llm = _get_llm_client()
    chunks = _chunk_text(text, llm.model)
    if not chunks:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF")

    summary = await _summarize_chunks(llm, chunks)
    entities = await _extract_entities(llm, chunks)
    action_plan = await _generate_action_plan(llm, summary, entities)

    artifacts = [
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "artifact_type": "summary",
            "title": "Document Summary",
            "content": summary,
            "created_at": datetime.utcnow().isoformat(),
            "review_status": REVIEW_PENDING,
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "artifact_type": "entities",
            "title": "Key Entities and Terms",
            "content": _format_entities(entities),
            "created_at": datetime.utcnow().isoformat(),
            "review_status": REVIEW_PENDING,
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "artifact_type": "action_plan",
            "title": "Action Plan",
            "content": action_plan,
            "created_at": datetime.utcnow().isoformat(),
            "review_status": REVIEW_PENDING,
        },
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "artifact_type": "full_text",
            "title": "Extracted Full Text",
            "content": text,
            "created_at": datetime.utcnow().isoformat(),
            "review_status": REVIEW_PENDING,
        },
    ]

    return artifacts


# =============================================================================
# Document Storage
# =============================================================================

def save_document_info(doc_info: dict) -> None:
    """Save document metadata."""
    doc_path = PROCESSED_DIR / f"{doc_info['id']}.json"
    with open(doc_path, 'w') as f:
        json.dump(doc_info, f, indent=2)


def load_document_info(doc_id: str) -> Optional[dict]:
    """Load document metadata."""
    doc_path = PROCESSED_DIR / f"{doc_id}.json"
    if doc_path.exists():
        with open(doc_path, 'r') as f:
            doc = json.load(f)
        if not isinstance(doc, dict):
            return None
        counts = _compute_review_counts(doc.get("artifacts", []))
        doc.update({k: doc.get(k, v) for k, v in counts.items()})
        return doc
    return None


def save_artifact(artifact: dict) -> None:
    """Save an artifact to disk."""
    artifact = _normalize_artifact(artifact)
    artifact_path = ARTIFACTS_DIR / f"{artifact['id']}.json"
    with open(artifact_path, 'w') as f:
        json.dump(artifact, f, indent=2)


def load_artifact(artifact_id: str) -> Optional[dict]:
    """Load an artifact from disk."""
    artifact_path = ARTIFACTS_DIR / f"{artifact_id}.json"
    if artifact_path.exists():
        with open(artifact_path, 'r') as f:
            return _normalize_artifact(json.load(f))
    return None


def _normalize_artifact(artifact: dict) -> dict:
    artifact.setdefault("review_status", REVIEW_PENDING)
    artifact.setdefault("reviewed_at", None)
    artifact.setdefault("reviewed_by", None)
    artifact.setdefault("review_notes", None)
    return artifact


def _compute_review_counts(artifact_ids: List[str]) -> Dict[str, int]:
    pending = 0
    reviewed = 0
    for artifact_id in artifact_ids:
        artifact = load_artifact(artifact_id)
        if not artifact:
            continue
        status = artifact.get("review_status", REVIEW_PENDING)
        if status in {REVIEW_PENDING, REVIEW_NEEDS_REVISION}:
            pending += 1
        elif status == REVIEW_REVIEWED:
            reviewed += 1
    total = len(artifact_ids)
    return {
        "review_pending_count": pending,
        "review_completed_count": reviewed,
        "review_total_count": total,
    }


def _update_document_review_counts(doc_id: str) -> None:
    doc = load_document_info(doc_id)
    if not doc:
        return
    counts = _compute_review_counts(doc.get("artifacts", []))
    doc.update(counts)
    save_document_info(doc)


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/upload", response_model=DocumentInfo)
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload a PDF document for processing.
    The document is processed synchronously to generate review-ready artifacts.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOADS_DIR / f"{doc_id}.pdf"
    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create document info
    doc_info = {
        "id": doc_id,
        "filename": file.filename,
        "status": "processing",
        "uploaded_at": datetime.utcnow().isoformat(),
        "artifacts": [],
        "review_pending_count": 0,
        "review_total_count": 0,
        "review_completed_count": 0,
    }
    
    # Process immediately (synchronous for now)
    try:
        # Extract text
        text, page_count = extract_text_from_pdf(file_path)
        doc_info["page_count"] = page_count
        doc_info["text_length"] = len(text)
        
        # Generate artifacts
        artifacts = await process_document(doc_id, text)
        
        # Save artifacts
        for artifact in artifacts:
            save_artifact(artifact)
            doc_info["artifacts"].append(artifact["id"])
        
        doc_info.update(_compute_review_counts(doc_info["artifacts"]))
        doc_info["status"] = "completed"
        doc_info["processed_at"] = datetime.utcnow().isoformat()
    except HTTPException as e:
        doc_info["status"] = "error"
        doc_info["error"] = e.detail
        save_document_info(doc_info)
        raise
    except Exception as e:
        doc_info["status"] = "error"
        doc_info["error"] = str(e)
        save_document_info(doc_info)
        raise HTTPException(status_code=500, detail=str(e)) from e

    # Save document info
    save_document_info(doc_info)

    return DocumentInfo(**doc_info)


@router.get("/", response_model=List[DocumentInfo])
async def list_documents():
    """List all uploaded documents."""
    documents = []
    for doc_file in PROCESSED_DIR.glob("*.json"):
        with open(doc_file, 'r') as f:
            doc = json.load(f)
        if isinstance(doc, dict):
            doc.update(_compute_review_counts(doc.get("artifacts", [])))
            documents.append(DocumentInfo(**doc))
    
    # Sort by upload date (newest first)
    documents.sort(key=lambda d: d.uploaded_at, reverse=True)
    return documents


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: str):
    """Get a specific document's info."""
    doc = load_document_info(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.update(_compute_review_counts(doc.get("artifacts", [])))
    return DocumentInfo(**doc)


@router.get("/{doc_id}/artifacts", response_model=List[ArtifactInfo])
async def get_document_artifacts(doc_id: str):
    """Get all artifacts for a document."""
    doc = load_document_info(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    artifacts = []
    for artifact_id in doc.get("artifacts", []):
        artifact = load_artifact(artifact_id)
        if artifact:
            artifacts.append(ArtifactInfo(**artifact))
    
    return artifacts


@router.get("/artifacts/{artifact_id}", response_model=ArtifactInfo)
async def get_artifact(artifact_id: str):
    """Get a specific artifact."""
    artifact = load_artifact(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactInfo(**artifact)


@router.put("/artifacts/{artifact_id}/review", response_model=ArtifactInfo)
async def update_artifact_review(artifact_id: str, payload: ArtifactReviewUpdate):
    """Update review status for a specific artifact."""
    artifact = load_artifact(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if payload.review_status not in {REVIEW_PENDING, REVIEW_REVIEWED, REVIEW_NEEDS_REVISION}:
        raise HTTPException(status_code=400, detail="Invalid review status")
    if payload.review_status == REVIEW_NEEDS_REVISION and not payload.review_notes:
        raise HTTPException(status_code=422, detail="Review notes are required for revisions")

    artifact["review_status"] = payload.review_status
    artifact["reviewed_by"] = payload.reviewed_by
    artifact["review_notes"] = payload.review_notes
    artifact["reviewed_at"] = (
        datetime.utcnow().isoformat() if payload.review_status != REVIEW_PENDING else None
    )
    save_artifact(artifact)
    _update_document_review_counts(artifact.get("document_id", ""))
    return ArtifactInfo(**artifact)


@router.get("/{doc_id}/file")
async def get_document_file(doc_id: str):
    """Stream the original PDF for inline viewing."""
    doc = load_document_info(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    pdf_path = UPLOADS_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    filename = doc.get("filename", f"{doc_id}.pdf")
    headers = {"Content-Disposition": f"inline; filename=\"{filename}\""}
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename, headers=headers)


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its artifacts."""
    doc = load_document_info(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete artifacts
    for artifact_id in doc.get("artifacts", []):
        artifact_path = ARTIFACTS_DIR / f"{artifact_id}.json"
        if artifact_path.exists():
            artifact_path.unlink()
    
    # Delete PDF
    pdf_path = UPLOADS_DIR / f"{doc_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()
    
    # Delete document info
    doc_path = PROCESSED_DIR / f"{doc_id}.json"
    if doc_path.exists():
        doc_path.unlink()
    
    return {"success": True, "message": "Document deleted"}
