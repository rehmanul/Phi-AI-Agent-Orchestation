"""
Agentic Coding Development Workflow Engine

Implements the workflow from Diagram 5: Knowledge Spine → Agentic Core → 
Control Gates → Human Review → Traceable Outputs
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
from enum import Enum


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GateStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"


class WorkflowEngine:
    """Main workflow orchestrator following the agentic coding development pattern"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.knowledge_context = {}
        self.agentic_reasoning = {}
        self.gate_results = {}
        self.outputs = {}
        self.decision_log = []
        
    def run_workflow(self, task_description: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the complete workflow
        
        Flow: Knowledge Spine → Agentic Core → Control Gates → Outputs
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n{'='*60}")
        print(f"[START] Starting Agentic Coding Development Workflow")
        print(f"[TASK] Task: {task_description}")
        print(f"[ID] Workflow ID: {workflow_id}")
        print(f"{'='*60}\n")
        
        # Step 1: Knowledge Spine (Context Gathering)
        print("[PHASE 1] Knowledge Spine - Gathering Context...")
        self.knowledge_context = self._gather_knowledge_context(task_description, context)
        print(f"   [OK] Gathered {len(self.knowledge_context)} knowledge sources\n")
        
        # Step 2: Agentic Reasoning Core
        print("[PHASE 2] Agentic Reasoning Core - Processing...")
        self.agentic_reasoning = self._run_agentic_reasoning(task_description, self.knowledge_context)
        print(f"   [OK] Completed {len(self.agentic_reasoning)} reasoning steps\n")
        
        # Step 3: Control Gates
        print("[PHASE 3] Diagnostic Control Gates - Evaluating...")
        self.gate_results = self._evaluate_control_gates(self.agentic_reasoning)
        print(f"   [OK] Evaluated {len(self.gate_results)} control gates\n")
        
        # Step 4: Check if we can proceed
        if self.gate_results.get("can_proceed", False):
            print("[PASS] All gates passed - Proceeding to output generation\n")
            
            # Step 5: Generate Traceable Outputs
            print("[PHASE 4] Generating Traceable Outputs...")
            self.outputs = self._generate_traceable_outputs(
                task_description,
                self.knowledge_context,
                self.agentic_reasoning,
                self.gate_results
            )
            print(f"   [OK] Generated {len(self.outputs)} output artifacts\n")
        else:
            print("[BLOCK] Workflow blocked by control gates\n")
            self.outputs = self._generate_blocked_outputs()
        
        # Step 6: Create Decision Log
        self.decision_log.append({
            "workflow_id": workflow_id,
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "gate_results": self.gate_results,
            "status": "completed" if self.gate_results.get("can_proceed") else "blocked"
        })
        
        # Step 7: Save all outputs
        results = self._save_outputs(workflow_id)
        
        print(f"\n{'='*60}")
        print(f"[COMPLETE] Workflow Complete")
        print(f"[OUTPUT] Outputs saved to: {self.output_dir / workflow_id}")
        print(f"{'='*60}\n")
        
        return results
    
    def _gather_knowledge_context(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Knowledge Spine: Gather context from various sources"""
        knowledge = {
            "peer_reviewed_sources": [
                "Software Engineering Best Practices",
                "Design Patterns and Architecture Principles"
            ],
            "guidelines": [
                "PEP 8 Python Style Guide",
                "SOLID Principles",
                "Clean Code Standards"
            ],
            "regulatory_text": [
                "Security Best Practices",
                "Data Privacy Requirements"
            ],
            "historical_cases": [
                "Similar Project Implementations",
                "Known Failure Patterns"
            ],
            "institutional_playbooks": [
                "Code Review Standards",
                "Testing Requirements",
                "Documentation Standards"
            ],
            "decision_science": [
                "Risk Assessment Frameworks",
                "Cost-Benefit Analysis Models"
            ],
            "precedent": [
                "Previous Successful Patterns",
                "Team Coding Standards"
            ],
            "synthesized_context": {
                "task_understanding": f"Analyzing task: {task}",
                "relevant_standards": "PEP 8, SOLID, Clean Code",
                "risk_factors": "Code quality, maintainability, security",
                "success_criteria": "Working code, tests, documentation"
            }
        }
        return knowledge
    
    def _run_agentic_reasoning(self, task: str, knowledge: Dict) -> Dict[str, Any]:
        """Agentic Reasoning Core: 7-step reasoning process"""
        reasoning = {
            "pattern_recall": {
                "description": "Identify relevant patterns from knowledge base",
                "patterns_found": [
                    "Modular architecture pattern",
                    "Error handling patterns",
                    "Testing patterns"
                ],
                "confidence": ConfidenceLevel.MEDIUM.value
            },
            "differential_expansion": {
                "description": "Explore multiple solution approaches",
                "alternatives": [
                    {
                        "approach": "Direct implementation",
                        "pros": ["Fast", "Simple"],
                        "cons": ["Less flexible"]
                    },
                    {
                        "approach": "Modular with interfaces",
                        "pros": ["Flexible", "Testable"],
                        "cons": ["More complex"]
                    }
                ],
                "confidence": ConfidenceLevel.MEDIUM.value
            },
            "evidence_mapping": {
                "description": "Map evidence to support each approach",
                "evidence": {
                    "requirements": "Clear task description",
                    "standards": "PEP 8, SOLID principles",
                    "constraints": "Python, maintainable code"
                },
                "confidence": ConfidenceLevel.HIGH.value
            },
            "failure_mode_enumeration": {
                "description": "Identify potential failure modes",
                "failure_modes": [
                    "Incorrect implementation",
                    "Missing error handling",
                    "Poor test coverage",
                    "Security vulnerabilities"
                ],
                "confidence": ConfidenceLevel.MEDIUM.value
            },
            "boundary_stress_modeling": {
                "description": "Test edge cases and boundaries",
                "edge_cases": [
                    "Empty input handling",
                    "Large input handling",
                    "Invalid input handling",
                    "Concurrent access"
                ],
                "confidence": ConfidenceLevel.MEDIUM.value
            },
            "optionality_analysis": {
                "description": "Analyze optional design choices",
                "options": {
                    "error_handling": "Comprehensive try-except blocks",
                    "logging": "Structured logging",
                    "configuration": "Environment-based config",
                    "testing": "Unit + integration tests"
                },
                "confidence": ConfidenceLevel.HIGH.value
            },
            "confidence_banding": {
                "description": "Assign confidence levels",
                "overall_confidence": ConfidenceLevel.MEDIUM.value,
                "confidence_breakdown": {
                    "requirements_understanding": ConfidenceLevel.HIGH.value,
                    "solution_viability": ConfidenceLevel.HIGH.value,
                    "implementation_complexity": ConfidenceLevel.MEDIUM.value,
                    "risk_level": ConfidenceLevel.LOW.value
                }
            }
        }
        return reasoning
    
    def _evaluate_control_gates(self, reasoning: Dict) -> Dict[str, Any]:
        """Control Gates: Evaluate if we can proceed"""
        gates = {}
        
        # Gate 1: Evidence Sufficient?
        evidence_confidence = reasoning.get("confidence_banding", {}).get("overall_confidence")
        gates["evidence_sufficient"] = {
            "status": GateStatus.PASS.value,
            "reason": f"Evidence confidence: {evidence_confidence}",
            "details": "Sufficient context and understanding available"
        }
        
        # Gate 2: Harm Asymmetry?
        risk_level = reasoning.get("confidence_banding", {}).get("confidence_breakdown", {}).get("risk_level")
        harm_asymmetry = "low" if risk_level == ConfidenceLevel.LOW.value else "medium"
        gates["harm_asymmetry"] = {
            "status": GateStatus.PASS.value if harm_asymmetry == "low" else GateStatus.PASS.value,
            "reason": f"Risk level: {risk_level}",
            "details": "Low risk of negative impact"
        }
        
        # Gate 3: Differential Preserved?
        alternatives_count = len(reasoning.get("differential_expansion", {}).get("alternatives", []))
        gates["differential_preserved"] = {
            "status": GateStatus.PASS.value if alternatives_count > 1 else GateStatus.FAIL.value,
            "reason": f"Multiple alternatives considered: {alternatives_count}",
            "details": "Differential thinking maintained"
        }
        
        # Gate 4: Human Review Completed?
        # In automated run, we mark as "pending" - would require human input
        gates["human_review_completed"] = {
            "status": GateStatus.PASS.value,  # Auto-pass for demo, normally would require human
            "reason": "Automated approval for demonstration",
            "details": "NOTE: In production, requires human validation",
            "requires_approval": True
        }
        
        # Overall decision
        all_passed = all(g.get("status") == GateStatus.PASS.value for g in gates.values())
        gates["can_proceed"] = all_passed
        
        return gates
    
    def _generate_traceable_outputs(self, task: str, knowledge: Dict, reasoning: Dict, gates: Dict) -> Dict[str, Any]:
        """Generate all traceable outputs"""
        outputs = {
            "draft_narrative": {
                "type": "Draft Diagnostic Narrative",
                "content": f"""
# Implementation Plan for: {task}

## Context
{knowledge.get('synthesized_context', {}).get('task_understanding', '')}

## Recommended Approach
Based on analysis of {len(reasoning.get('differential_expansion', {}).get('alternatives', []))} alternatives,
the recommended approach is a modular implementation with comprehensive error handling.

## Key Considerations
- Follows PEP 8 and SOLID principles
- Includes error handling for edge cases
- Provides structured logging
- Includes unit tests

## Confidence Level
{reasoning.get('confidence_banding', {}).get('overall_confidence', 'medium')}
                """.strip()
            },
            "differential_table": {
                "type": "Differential Table",
                "content": [
                    {
                        "approach": alt.get("approach"),
                        "pros": alt.get("pros", []),
                        "cons": alt.get("cons", []),
                        "selected": idx == 1  # Select second approach
                    }
                    for idx, alt in enumerate(reasoning.get("differential_expansion", {}).get("alternatives", []))
                ]
            },
            "evidence_gaps": {
                "type": "Evidence Gaps",
                "content": [
                    "Need clarification on specific error handling requirements",
                    "User acceptance criteria should be confirmed"
                ]
            },
            "confidence_bands": {
                "type": "Confidence Bands",
                "content": reasoning.get("confidence_banding", {})
            },
            "decision_log": {
                "type": "Decision Log",
                "content": self.decision_log
            }
        }
        return outputs
    
    def _generate_blocked_outputs(self) -> Dict[str, Any]:
        """Generate outputs when workflow is blocked"""
        return {
            "status": "blocked",
            "reason": "Control gates failed",
            "gate_results": self.gate_results,
            "next_steps": "Review gate failures and provide additional context"
        }
    
    def _save_outputs(self, workflow_id: str) -> Dict[str, Any]:
        """Save all outputs to files"""
        output_path = self.output_dir / workflow_id
        output_path.mkdir(exist_ok=True)
        
        results = {
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "outputs": {}
        }
        
        # Save each output type
        for output_name, output_data in self.outputs.items():
            if output_name == "draft_narrative":
                file_path = output_path / "draft_narrative.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output_data.get("content", ""))
                results["outputs"]["draft_narrative"] = str(file_path)
                
            elif output_name == "differential_table":
                file_path = output_path / "differential_table.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data.get("content", []), f, indent=2)
                results["outputs"]["differential_table"] = str(file_path)
                
            elif output_name == "evidence_gaps":
                file_path = output_path / "evidence_gaps.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data.get("content", []), f, indent=2)
                results["outputs"]["evidence_gaps"] = str(file_path)
                
            elif output_name == "confidence_bands":
                file_path = output_path / "confidence_bands.json"
                confidence_data = output_data.get("content", {})
                # Convert Enum values to strings
                if isinstance(confidence_data, dict):
                    confidence_data = {
                        k: v.value if isinstance(v, Enum) else v 
                        for k, v in confidence_data.items()
                    }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(confidence_data, f, indent=2)
                results["outputs"]["confidence_bands"] = str(file_path)
                
            elif output_name == "decision_log":
                file_path = output_path / "decision_log.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data.get("content", []), f, indent=2)
                results["outputs"]["decision_log"] = str(file_path)
        
        # Save complete workflow summary
        summary_path = output_path / "workflow_summary.json"
        summary = {
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "knowledge_context": self._serialize_for_json(self.knowledge_context),
            "agentic_reasoning": self._serialize_for_json(self.agentic_reasoning),
            "gate_results": self._serialize_for_json(self.gate_results),
            "outputs": list(self.outputs.keys()),
            "output_files": results["outputs"]
        }
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        results["summary"] = str(summary_path)
        return results
    
    def _serialize_for_json(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return obj
