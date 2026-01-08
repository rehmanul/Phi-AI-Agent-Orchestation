"""
Process a PDF through the complete document intelligence pipeline
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Import all processing components
from agents.parsing.pdf_parser import PDFParser
from agents.classification.doc_type_classifier import DocumentTypeClassifier
from agents.classification.llm_router import LLMRouter
from agents.ml.ner_extractor import NERExtractor
from agents.ml.similarity_analyzer import SimilarityAnalyzer
from agents.ml.topic_tagger import TopicTagger
from agents.ml.outlier_detector import OutlierDetector
from agents.normalization.table_normalizer import TableNormalizer
from agents.intelligence.price_band_agent import PriceBandAgent
from agents.intelligence.motivation_classifier import MotivationClassifier
from agents.utils.confidence_metadata import ConfidenceMetadata

# Input PDF path
INPUT_PDF = Path(r"C:\Users\phi3t\12.20 dash\1.5.2026\PDF HTML TRAINING PHI ADD IN\BILLS-119s1071enr.pdf")

# Output directory
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Processing directories
PARSED_DIR = OUTPUT_DIR / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = OUTPUT_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def main():
    """Process PDF through complete pipeline"""
    
    document_id = "processed_document"
    processing_log = {
        "document_id": document_id,
        "input_file": str(INPUT_PDF),
        "processing_started": datetime.utcnow().isoformat(),
        "stages": [],
        "models_used": [],
        "outputs": {}
    }
    
    print(f"Processing PDF: {INPUT_PDF.name}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 60)
    
    # Stage 1: PDF Parsing
    print("\n[1/9] Parsing PDF...")
    try:
        parser = PDFParser(PARSED_DIR)
        parse_result = parser.parse(INPUT_PDF, document_id)
        processing_log["stages"].append({
            "stage": "pdf_parsing",
            "status": "success",
            "model": parse_result.get("pdf_mode", "unknown"),
            "outputs": parse_result.get("artifacts", {})
        })
        processing_log["models_used"].append("pdfplumber/PyMuPDF (PDF parsing)")
        if parse_result.get("pdf_mode") == "scanned":
            processing_log["models_used"].append("Tesseract OCR (scanned PDF)")
        print(f"  ✓ Parsed {parse_result.get('pdf_mode', 'unknown')} PDF")
        print(f"  ✓ Extracted text, layout, tables")
    except Exception as e:
        print(f"  ✗ Parsing failed: {e}")
        processing_log["stages"].append({
            "stage": "pdf_parsing",
            "status": "error",
            "error": str(e)
        })
        return processing_log
    
    # Load parsed text
    parsed_text_file = PARSED_DIR / f"{document_id}_parsed_text.json"
    if parsed_text_file.exists():
        with open(parsed_text_file, "r", encoding="utf-8") as f:
            parsed_text = json.load(f)
    else:
        print("  ✗ Parsed text file not found")
        return processing_log
    
    # Stage 2: Document Classification
    print("\n[2/9] Classifying document type...")
    try:
        classifier = DocumentTypeClassifier()
        classification = classifier.classify(parsed_text, INPUT_PDF.name)
        processing_log["stages"].append({
            "stage": "document_classification",
            "status": "success",
            "model": "rule_based",
            "document_type": classification.get("document_type"),
            "confidence": classification.get("confidence")
        })
        processing_log["models_used"].append("Rule-based classifier (document type)")
        print(f"  ✓ Document type: {classification.get('document_type')} (confidence: {classification.get('confidence')})")
        
        # Save classification
        classification_file = PROCESSED_DIR / f"{document_id}_classification.json"
        with open(classification_file, "w") as f:
            json.dump(classification, f, indent=2)
        processing_log["outputs"]["classification"] = str(classification_file)
    except Exception as e:
        print(f"  ✗ Classification failed: {e}")
        processing_log["stages"].append({"stage": "document_classification", "status": "error", "error": str(e)})
    
    # Stage 3: LLM Router
    print("\n[3/9] Routing to ML pipelines...")
    try:
        router = LLMRouter()  # No API key = rule-based
        parsed_layout_file = PARSED_DIR / f"{document_id}_parsed_layout.json"
        parsed_tables_file = PARSED_DIR / f"{document_id}_parsed_tables.json"
        
        parsed_layout = None
        parsed_tables = None
        
        if parsed_layout_file.exists():
            with open(parsed_layout_file, "r") as f:
                parsed_layout = json.load(f)
        
        if parsed_tables_file.exists():
            with open(parsed_tables_file, "r") as f:
                parsed_tables = json.load(f)
        
        routing = router.suggest_pipelines(
            classification.get("document_type", "unknown"),
            parsed_text,
            parsed_layout,
            parsed_tables
        )
        processing_log["stages"].append({
            "stage": "pipeline_routing",
            "status": "success",
            "model": routing.get("routing_method", "rule_based"),
            "pipelines_suggested": routing.get("total_pipelines", 0)
        })
        processing_log["models_used"].append(f"{routing.get('routing_method', 'rule_based')} router")
        print(f"  ✓ Suggested {routing.get('total_pipelines', 0)} ML pipelines")
        
        # Save routing
        routing_file = PROCESSED_DIR / f"{document_id}_routing.json"
        with open(routing_file, "w") as f:
            json.dump(routing, f, indent=2)
        processing_log["outputs"]["routing"] = str(routing_file)
    except Exception as e:
        print(f"  ✗ Routing failed: {e}")
        processing_log["stages"].append({"stage": "pipeline_routing", "status": "error", "error": str(e)})
    
    # Stage 4: NER Extraction
    print("\n[4/9] Extracting named entities...")
    try:
        ner_extractor = NERExtractor(model="spacy")
        entities = ner_extractor.extract(parsed_text)
        processing_log["stages"].append({
            "stage": "ner_extraction",
            "status": "success",
            "model": entities.get("model", "rule_based"),
            "entities_found": entities.get("total_entities", 0)
        })
        processing_log["models_used"].append(f"{entities.get('model', 'rule_based')} (NER)")
        print(f"  ✓ Extracted {entities.get('total_entities', 0)} entities")
        
        # Save entities
        entities_file = PROCESSED_DIR / f"{document_id}_entities.json"
        with open(entities_file, "w") as f:
            json.dump(entities, f, indent=2)
        processing_log["outputs"]["entities"] = str(entities_file)
    except Exception as e:
        print(f"  ✗ NER extraction failed: {e}")
        processing_log["stages"].append({"stage": "ner_extraction", "status": "error", "error": str(e)})
        entities = None
    
    # Stage 5: Topic Tagging
    print("\n[5/9] Tagging topics...")
    try:
        tagger = TopicTagger()
        tags = tagger.tag(parsed_text)
        processing_log["stages"].append({
            "stage": "topic_tagging",
            "status": "success",
            "model": "rule_based",
            "topics_found": tags.get("total_tags", 0)
        })
        processing_log["models_used"].append("Rule-based topic tagger")
        print(f"  ✓ Tagged {tags.get('total_tags', 0)} topics")
        
        # Save tags
        tags_file = PROCESSED_DIR / f"{document_id}_tags.json"
        with open(tags_file, "w") as f:
            json.dump(tags, f, indent=2)
        processing_log["outputs"]["tags"] = str(tags_file)
    except Exception as e:
        print(f"  ✗ Topic tagging failed: {e}")
        processing_log["stages"].append({"stage": "topic_tagging", "status": "error", "error": str(e)})
        tags = None
    
    # Stage 6: Table Normalization
    print("\n[6/9] Normalizing tables...")
    try:
        if parsed_tables and parsed_tables.get("total_tables", 0) > 0:
            normalizer = TableNormalizer()
            normalized = normalizer.normalize(parsed_tables, output_format="json")
            processing_log["stages"].append({
                "stage": "table_normalization",
                "status": "success",
                "model": "pandas",
                "tables_normalized": normalized.get("total_tables", 0)
            })
            processing_log["models_used"].append("pandas (table normalization)")
            print(f"  ✓ Normalized {normalized.get('total_tables', 0)} tables")
            
            # Save normalized tables
            tables_file = PROCESSED_DIR / f"{document_id}_tables_normalized.json"
            with open(tables_file, "w") as f:
                json.dump(normalized, f, indent=2)
            processing_log["outputs"]["tables"] = str(tables_file)
        else:
            print("  ⚠ No tables found in document")
            processing_log["stages"].append({
                "stage": "table_normalization",
                "status": "skipped",
                "reason": "No tables found"
            })
    except Exception as e:
        print(f"  ✗ Table normalization failed: {e}")
        processing_log["stages"].append({"stage": "table_normalization", "status": "error", "error": str(e)})
    
    # Stage 7: Price Band Inference
    print("\n[7/9] Inferring price band...")
    try:
        price_agent = PriceBandAgent()  # No API key = rule-based
        price_band = price_agent.infer_price_band(parsed_text, entities, parsed_tables)
        processing_log["stages"].append({
            "stage": "price_band_inference",
            "status": "success",
            "model": price_band.get("method", "rule_based"),
            "confidence": price_band.get("confidence", 0)
        })
        processing_log["models_used"].append(f"{price_band.get('method', 'rule_based')} (price inference)")
        if price_band.get("price_min"):
            print(f"  ✓ Price band: ${price_band.get('price_min'):,.0f} - ${price_band.get('price_max'):,.0f}")
        else:
            print("  ⚠ No price information found")
        
        # Save price band
        price_file = PROCESSED_DIR / f"{document_id}_price_band.json"
        with open(price_file, "w") as f:
            json.dump(price_band, f, indent=2)
        processing_log["outputs"]["price_band"] = str(price_file)
    except Exception as e:
        print(f"  ✗ Price band inference failed: {e}")
        processing_log["stages"].append({"stage": "price_band_inference", "status": "error", "error": str(e)})
        price_band = None
    
    # Stage 8: Motivation Classification
    print("\n[8/9] Classifying owner motivation...")
    try:
        motivation_classifier = MotivationClassifier()  # No API key = rule-based
        motivation = motivation_classifier.classify(parsed_text, sell_score=75.0, entities=entities)
        processing_log["stages"].append({
            "stage": "motivation_classification",
            "status": "success",
            "model": motivation.get("method", "rule_based"),
            "primary_motivation": motivation.get("primary_motivation")
        })
        processing_log["models_used"].append(f"{motivation.get('method', 'rule_based')} (motivation classification)")
        print(f"  ✓ Primary motivation: {motivation.get('primary_motivation', 'unknown')}")
        
        # Save motivation
        motivation_file = PROCESSED_DIR / f"{document_id}_motivation.json"
        with open(motivation_file, "w") as f:
            json.dump(motivation, f, indent=2)
        processing_log["outputs"]["motivation"] = str(motivation_file)
    except Exception as e:
        print(f"  ✗ Motivation classification failed: {e}")
        processing_log["stages"].append({"stage": "motivation_classification", "status": "error", "error": str(e)})
    
    # Stage 9: Confidence Metadata
    print("\n[9/9] Attaching confidence metadata...")
    try:
        confidence_manager = ConfidenceMetadata(PROCESSED_DIR)
        
        # Aggregate confidence from all stages
        all_artifacts = {}
        if entities:
            all_artifacts["entities"] = confidence_manager.attach_confidence(
                "entities", entities, 0.8, 85.0
            )
        if tags:
            all_artifacts["tags"] = confidence_manager.attach_confidence(
                "tags", tags, 0.7, 70.0
            )
        
        aggregated = confidence_manager.aggregate_confidence(all_artifacts)
        processing_log["stages"].append({
            "stage": "confidence_metadata",
            "status": "success",
            "average_confidence": aggregated.get("average_confidence", 0)
        })
        print(f"  ✓ Average confidence: {aggregated.get('average_confidence', 0):.2f}")
        
        # Save confidence
        confidence_file = PROCESSED_DIR / f"{document_id}_confidence.json"
        with open(confidence_file, "w") as f:
            json.dump(aggregated, f, indent=2)
        processing_log["outputs"]["confidence"] = str(confidence_file)
    except Exception as e:
        print(f"  ✗ Confidence metadata failed: {e}")
        processing_log["stages"].append({"stage": "confidence_metadata", "status": "error", "error": str(e)})
    
    # Finalize
    processing_log["processing_completed"] = datetime.utcnow().isoformat()
    processing_log["total_stages"] = len(processing_log["stages"])
    processing_log["successful_stages"] = len([s for s in processing_log["stages"] if s.get("status") == "success"])
    
    # Save processing log
    log_file = OUTPUT_DIR / "processing_log.json"
    with open(log_file, "w") as f:
        json.dump(processing_log, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"  Stages: {processing_log['successful_stages']}/{processing_log['total_stages']} successful")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    
    return processing_log

if __name__ == "__main__":
    result = main()
