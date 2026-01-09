"""
Document Processing API Routes

Provides endpoints for:
- PDF upload and text extraction
- Document processing pipeline
- Viewing generated artifacts
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
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

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "that", "the", "to", "was", "were",
    "with", "this", "these", "those", "will", "shall", "may", "must", "not", "no",
    "such", "their", "they", "them", "he", "she", "we", "our", "you", "your",
    "which", "who", "whom", "what", "when", "where", "why", "how", "if", "then",
    "also", "any", "all", "can", "could", "should", "would", "than", "into", "over",
    "under", "up", "down", "out", "about", "there", "here", "after", "before",
}

AGENCY_NAMES = [
    "Federal Communications Commission",
    "Federal Trade Commission",
    "Department of Energy",
    "Department of Commerce",
    "Department of Transportation",
    "Department of Homeland Security",
    "Department of Justice",
    "Department of Defense",
    "Environmental Protection Agency",
    "Office of Management and Budget",
    "Office of Science and Technology Policy",
    "National Institute of Standards and Technology",
    "National Telecommunications and Information Administration",
    "Securities and Exchange Commission",
    "Federal Energy Regulatory Commission",
]

STATE_NAMES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]

MONTHS = (
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
)


def _normalize_text(text: str) -> str:
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split())


def _split_sentences(text: str) -> List[str]:
    import re

    normalized = _normalize_text(text)
    if not normalized:
        return []
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", normalized)
    cleaned = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 30:
            continue
        cleaned.append(sentence)
    return cleaned


def _tokenize_words(text: str) -> List[str]:
    import re

    return re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']+", text.lower())


def _word_frequencies(words: List[str]) -> Dict[str, float]:
    freq: Dict[str, float] = {}
    for word in words:
        if word in STOPWORDS or len(word) < 3:
            continue
        freq[word] = freq.get(word, 0.0) + 1.0
    if not freq:
        return freq
    max_freq = max(freq.values())
    for word in list(freq.keys()):
        freq[word] = freq[word] / max_freq
    return freq


def _score_sentences(sentences: List[str], word_scores: Dict[str, float]) -> Dict[int, float]:
    import re

    scores: Dict[int, float] = {}
    for idx, sentence in enumerate(sentences):
        words = _tokenize_words(sentence)
        if not words:
            continue
        score = sum(word_scores.get(word, 0.0) for word in words)
        score = score / max(len(words), 1)
        if idx < 5:
            score *= 1.2
        if re.search(r"\b(section|title|chapter|rule|regulation|statute|requirement)\b", sentence, re.I):
            score *= 1.15
        scores[idx] = score
    return scores


def _select_summary(sentences: List[str], scores: Dict[int, float]) -> List[str]:
    if not sentences:
        return []
    target = max(4, min(12, len(sentences) // 8 or 4))
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    selected_idx = sorted([idx for idx, _ in ranked[:target]])
    return [sentences[idx] for idx in selected_idx]


def _extract_headings(text: str) -> List[str]:
    headings = []
    for line in text.splitlines():
        line = line.strip()
        if not line or len(line) > 120:
            continue
        if line.isupper() and len(line) > 5:
            headings.append(line)
        elif line.endswith(":") and len(line) > 5:
            headings.append(line.rstrip(":"))
    return headings[:12]


def _extract_key_terms(text: str, limit: int = 15) -> List[str]:
    words = _tokenize_words(text)
    freq = _word_frequencies(words)
    ranked = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    return [term for term, _ in ranked[:limit]]


def _extract_entities(text: str) -> Dict[str, List[str]]:
    import re

    entities: Dict[str, set] = {
        "People": set(),
        "Organizations": set(),
        "Agencies": set(),
        "Legal References": set(),
        "Dates": set(),
        "Monetary Values": set(),
        "Locations": set(),
        "Key Terms": set(),
    }

    for agency in AGENCY_NAMES:
        if re.search(re.escape(agency), text, re.I):
            entities["Agencies"].add(agency)

    for state in STATE_NAMES:
        if re.search(rf"\b{re.escape(state)}\b", text):
            entities["Locations"].add(state)

    month_pattern = r"|".join(MONTHS)
    date_patterns = [
        rf"\b(?:{month_pattern})\s+\d{{1,2}}(?:,\s*\d{{4}})?\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ]
    for pattern in date_patterns:
        for match in re.findall(pattern, text):
            entities["Dates"].add(match)

    money_pattern = r"\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand))?"
    for match in re.findall(money_pattern, text, re.I):
        entities["Monetary Values"].add(match)

    legal_patterns = [
        r"\b(?:Section|Sec\.|Title|Chapter|Article)\s+\d+[A-Za-z0-9\-\.]*",
        r"\b\d+\s+U\.S\.C\.?\s+(?:Section\s+)?\d+[A-Za-z0-9\-]*",
        r"\b\d+\s+C\.F\.R\.?\s+(?:Section\s+)?\d+[A-Za-z0-9\-]*",
        r"\b(?:H\.R\.|S\.)\s*\d+",
    ]
    for pattern in legal_patterns:
        for match in re.findall(pattern, text, re.I):
            entities["Legal References"].add(match)

    org_pattern = r"(?:[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,4})(?:\s+(?:Inc|LLC|Corp|Commission|Agency|Department|Administration|Authority|Council|Board|Office|Institute|Association))?"
    for match in re.findall(org_pattern, text):
        if len(match.split()) >= 2:
            entities["Organizations"].add(match)

    people_pattern = r"(?:Senator|Sen\.|Representative|Rep\.|Chair|Secretary|Director|Mr\.|Ms\.|Dr\.)\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?"
    for match in re.findall(people_pattern, text):
        entities["People"].add(match)

    entities["Key Terms"].update(_extract_key_terms(text))

    return {key: sorted(list(values)) for key, values in entities.items() if values}


def _format_entities(entities: Dict[str, List[str]]) -> str:
    if not entities:
        return "## Extracted Entities\n\nNo entities detected."
    output = "## Extracted Entities\n\n"
    for key in sorted(entities.keys()):
        output += f"### {key}\n"
        for item in entities[key]:
            output += f"- {item}\n"
        output += "\n"
    return output.strip()


def _extract_obligations(sentences: List[str]) -> List[str]:
    import re

    keywords = re.compile(
        r"\b(shall|must|required|is required|are required|prohibited|may not|must not|no later than|deadline|due by|effective on|effective date|compliance|submit|file|report|certify)\b",
        re.I,
    )
    obligations = []
    for sentence in sentences:
        if keywords.search(sentence):
            obligations.append(sentence)
    return obligations


def _classify_timeframe(sentence: str) -> str:
    import re

    match = re.search(r"within\s+(\d{1,3})\s+days", sentence, re.I)
    if match:
        days = int(match.group(1))
        if days <= 30:
            return "Immediate"
        if days <= 90:
            return "Mid-Term"
        return "Long-Term"
    if re.search(r"(annually|quarterly|monthly|ongoing)", sentence, re.I):
        return "Ongoing"
    if re.search(r"no later than|due by|effective on|effective date", sentence, re.I):
        return "Deadline"
    return "Required"


def _build_action_plan(text: str, sentences: List[str], entities: Dict[str, List[str]]) -> str:
    obligations = _extract_obligations(sentences)
    grouped: Dict[str, List[str]] = {
        "Immediate Actions (0-30 days)": [],
        "Mid-Term Actions (31-90 days)": [],
        "Long-Term or Ongoing Actions": [],
        "Deadline-Driven Actions": [],
        "Required Actions": [],
    }
    for obligation in obligations:
        bucket = _classify_timeframe(obligation)
        if bucket == "Immediate":
            grouped["Immediate Actions (0-30 days)"].append(obligation)
        elif bucket == "Mid-Term":
            grouped["Mid-Term Actions (31-90 days)"].append(obligation)
        elif bucket == "Long-Term" or bucket == "Ongoing":
            grouped["Long-Term or Ongoing Actions"].append(obligation)
        elif bucket == "Deadline":
            grouped["Deadline-Driven Actions"].append(obligation)
        else:
            grouped["Required Actions"].append(obligation)

    engagement_targets = entities.get("Agencies", []) + entities.get("Organizations", [])
    engagement = [f"Coordinate with {target}." for target in engagement_targets[:10]]

    risk_items = [
        sentence for sentence in sentences
        if any(term in sentence.lower() for term in ["penalty", "fine", "enforcement", "liability", "violation"])
    ]

    output = "## Action Plan\n\n"
    for section, items in grouped.items():
        if not items:
            continue
        output += f"### {section}\n"
        for idx, item in enumerate(items, 1):
            output += f"{idx}. {item}\n"
        output += "\n"

    if engagement:
        output += "### Stakeholder Engagement\n"
        for idx, item in enumerate(engagement, 1):
            output += f"{idx}. {item}\n"
        output += "\n"

    if risk_items:
        output += "### Risks and Enforcement\n"
        for idx, item in enumerate(risk_items[:10], 1):
            output += f"{idx}. {item}\n"
        output += "\n"

    if not obligations:
        output += "### Required Actions\n"
        output += "No explicit compliance obligations were detected in the extracted text. Review the PDF for implicit requirements.\n"

    return output.strip()


def process_document(doc_id: str, text: str) -> List[dict]:
    """
    Process extracted text and generate artifacts using local analysis.
    """
    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF")

    sentences = _split_sentences(text)
    word_scores = _word_frequencies(_tokenize_words(text))
    sentence_scores = _score_sentences(sentences, word_scores)
    summary_sentences = _select_summary(sentences, sentence_scores)
    headings = _extract_headings(text)

    summary_output = "## Document Overview\n\n"
    if headings:
        summary_output += "### Key Sections\n"
        for heading in headings:
            summary_output += f"- {heading}\n"
        summary_output += "\n"

    if summary_sentences:
        summary_output += "### Summary\n"
        for sentence in summary_sentences:
            summary_output += f"- {sentence}\n"
        summary_output += "\n"

    key_terms = _extract_key_terms(text)
    if key_terms:
        summary_output += "### Key Terms\n"
        for term in key_terms:
            summary_output += f"- {term}\n"
        summary_output += "\n"

    entities = _extract_entities(text)
    action_plan = _build_action_plan(text, sentences, entities)

    artifacts = [
        {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "artifact_type": "summary",
            "title": "Document Summary",
            "content": summary_output.strip(),
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
        artifacts = process_document(doc_id, text)
        
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
