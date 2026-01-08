"""
Document Processing API Routes

Provides endpoints for:
- PDF upload and text extraction
- Document processing pipeline
- Viewing generated artifacts
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel

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


class ArtifactInfo(BaseModel):
    id: str
    document_id: str
    artifact_type: str  # analysis, summary, brief, action_plan, etc.
    title: str
    content: str
    created_at: str


class ProcessingResult(BaseModel):
    document_id: str
    status: str
    message: str
    artifacts: List[str] = []


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


def process_document(doc_id: str, text: str) -> List[dict]:
    """
    Process extracted text and generate artifacts.
    This is a simplified local processor that doesn't require API keys.
    """
    artifacts = []
    
    # 1. Document Summary (basic extraction)
    summary_artifact = {
        "id": str(uuid.uuid4()),
        "document_id": doc_id,
        "artifact_type": "summary",
        "title": "Document Summary",
        "content": generate_summary(text),
        "created_at": datetime.utcnow().isoformat(),
    }
    artifacts.append(summary_artifact)
    
    # 2. Key Entities Extraction
    entities_artifact = {
        "id": str(uuid.uuid4()),
        "document_id": doc_id,
        "artifact_type": "entities",
        "title": "Key Entities & Terms",
        "content": extract_key_entities(text),
        "created_at": datetime.utcnow().isoformat(),
    }
    artifacts.append(entities_artifact)
    
    # 3. Action Items (if any legislative content detected)
    if any(word in text.lower() for word in ['bill', 'law', 'regulation', 'amendment', 'section', 'statute']):
        action_artifact = {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "artifact_type": "action_plan",
            "title": "Legislative Action Items",
            "content": generate_action_items(text),
            "created_at": datetime.utcnow().isoformat(),
        }
        artifacts.append(action_artifact)
    
    # 4. Full Text Reference
    text_artifact = {
        "id": str(uuid.uuid4()),
        "document_id": doc_id,
        "artifact_type": "full_text",
        "title": "Extracted Full Text",
        "content": text[:50000],  # Limit to 50k chars
        "created_at": datetime.utcnow().isoformat(),
    }
    artifacts.append(text_artifact)
    
    return artifacts


def generate_summary(text: str) -> str:
    """Generate a basic summary from text (no LLM required)."""
    lines = text.split('\n')
    
    # Find potential title/header lines
    headers = []
    for line in lines[:50]:
        line = line.strip()
        if line and len(line) < 200 and line[0].isupper():
            headers.append(line)
    
    # Get first substantial paragraphs
    paragraphs = []
    for line in lines:
        line = line.strip()
        if len(line) > 100:
            paragraphs.append(line)
            if len(paragraphs) >= 5:
                break
    
    summary = "## Document Overview\n\n"
    
    if headers:
        summary += "### Key Sections\n"
        for h in headers[:10]:
            summary += f"- {h}\n"
        summary += "\n"
    
    if paragraphs:
        summary += "### Content Preview\n\n"
        for p in paragraphs[:3]:
            summary += f"{p[:500]}...\n\n"
    
    summary += f"\n---\n*Document contains {len(text):,} characters across {len(lines):,} lines.*"
    
    return summary


def extract_key_entities(text: str) -> str:
    """Extract key entities from text (basic pattern matching)."""
    import re
    
    entities = {
        "Organizations": set(),
        "Legal References": set(),
        "Monetary Values": set(),
        "Dates": set(),
        "Key Terms": set(),
    }
    
    # Organizations (capitalized phrases)
    org_patterns = re.findall(r'(?:The\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}(?:\s+(?:Inc|LLC|Corp|Commission|Agency|Department|Act|Bill))?', text)
    for org in org_patterns[:20]:
        if len(org) > 5:
            entities["Organizations"].add(org)
    
    # Legal references
    legal_patterns = re.findall(r'(?:Section|§|Title|Chapter|Article|Bill|H\.R\.|S\.)\s*\d+[\w\-\.]*', text, re.IGNORECASE)
    entities["Legal References"] = set(legal_patterns[:15])
    
    # Monetary values
    money_patterns = re.findall(r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand))?', text, re.IGNORECASE)
    entities["Monetary Values"] = set(money_patterns[:10])
    
    # Dates
    date_patterns = re.findall(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', text)
    entities["Dates"] = set(date_patterns[:10])
    
    # Format output
    output = "## Extracted Entities\n\n"
    for category, items in entities.items():
        if items:
            output += f"### {category}\n"
            for item in sorted(items)[:15]:
                output += f"- {item}\n"
            output += "\n"
    
    return output


def generate_action_items(text: str) -> str:
    """Generate action items for legislative content."""
    output = "## Recommended Actions\n\n"
    
    text_lower = text.lower()
    
    actions = []
    
    if 'deadline' in text_lower or 'by date' in text_lower:
        actions.append("Review and note all compliance deadlines")
    
    if 'comment' in text_lower and 'period' in text_lower:
        actions.append("Prepare public comment submission before comment period closes")
    
    if 'stakeholder' in text_lower:
        actions.append("Identify and engage key stakeholders")
    
    if 'amendment' in text_lower:
        actions.append("Draft proposed amendments for review")
    
    if 'testimony' in text_lower or 'hearing' in text_lower:
        actions.append("Prepare testimony for upcoming hearings")
    
    if 'wireless' in text_lower or 'power' in text_lower or 'energy' in text_lower:
        actions.append("Coordinate with technical team on wireless power policy implications")
    
    # Default actions
    if not actions:
        actions = [
            "Review document with legal team",
            "Summarize key points for stakeholders",
            "Identify relevant policy impacts",
            "Schedule follow-up strategy session",
        ]
    
    for i, action in enumerate(actions, 1):
        output += f"{i}. **{action}**\n"
    
    output += "\n---\n*These are preliminary recommendations based on document content.*"
    
    return output


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
            return json.load(f)
    return None


def save_artifact(artifact: dict) -> None:
    """Save an artifact to disk."""
    artifact_path = ARTIFACTS_DIR / f"{artifact['id']}.json"
    with open(artifact_path, 'w') as f:
        json.dump(artifact, f, indent=2)


def load_artifact(artifact_id: str) -> Optional[dict]:
    """Load an artifact from disk."""
    artifact_path = ARTIFACTS_DIR / f"{artifact_id}.json"
    if artifact_path.exists():
        with open(artifact_path, 'r') as f:
            return json.load(f)
    return None


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/upload", response_model=DocumentInfo)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a PDF document for processing.
    The document will be processed in the background.
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
    }
    
    # Process immediately (synchronous for now)
    try:
        # Extract text
        text, page_count = extract_text_from_pdf(file_path)
        doc_info["page_count"] = page_count
        doc_info["text_length"] = len(text)
        
        # Generate artifacts
        artifacts = process_document(doc_id, text)
        
        # Save artifacts
        for artifact in artifacts:
            save_artifact(artifact)
            doc_info["artifacts"].append(artifact["id"])
        
        doc_info["status"] = "completed"
        doc_info["processed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        doc_info["status"] = "error"
        doc_info["error"] = str(e)
    
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
