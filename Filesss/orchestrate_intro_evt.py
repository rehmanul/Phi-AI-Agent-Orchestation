"""
Orchestration Script for INTRO_EVT Phase
Spawns intelligence agents first, then drafting agents after intelligence data is available.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
DASHBOARD_PATH = BASE_DIR / "monitoring" / "dashboard-status.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"


def log_event(event_type, message, **kwargs):
    """Log event to audit log."""
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "agent_id": "orchestrator",
        "message": message,
        **kwargs,
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def check_monitoring():
    """Check if monitoring dashboard is running."""
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
        return dashboard.get("overall_status") is not None
    except Exception:
        return False


def check_state():
    """Verify current state is INTRO_EVT."""
    try:
        # Try to use StateManager if available (API-based)
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(BASE_DIR))
            from app.storage import WorkflowStorage
            from app.state_manager import StateManager
            
            # Initialize storage and state manager
            data_dir = BASE_DIR / "data"
            storage = WorkflowStorage(data_dir)
            state_manager = StateManager(storage, STATE_PATH)
            
            current_state = state_manager.get_current_state()
            if current_state:
                return current_state.value == "INTRO_EVT"
        except Exception as e:
            # Fallback to file-based check
            pass
        
        # Fallback: read from file directly
        state = json.loads(STATE_PATH.read_text())
        return state.get("current_state") == "INTRO_EVT"
    except Exception:
        return False


def spawn_agent(agent_script):
    """Spawn an agent by running its script."""
    agent_path = BASE_DIR / "agents" / agent_script
    if not agent_path.exists():
        print(f"ERROR: Agent script not found: {agent_path}")
        return False

    print(f"Spawning agent: {agent_script}")
    try:
        result = subprocess.run(
            ["python", str(agent_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print(f"[OK] Agent {agent_script} completed successfully")
            return True
        else:
            print(f"[ERR] Agent {agent_script} failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[ERR] Agent {agent_script} timed out")
        return False
    except Exception as e:
        print(f"[ERR] Error spawning agent {agent_script}: {e}")
        return False


def check_intelligence_artifacts():
    """Check if intelligence artifacts are available."""
    required_artifacts = [
        BASE_DIR
        / "artifacts"
        / "intel_signal_scan_intro_evt"
        / "signal_summary.json",
        BASE_DIR
        / "artifacts"
        / "intel_stakeholder_map_intro_evt"
        / "PRE_STAKEHOLDER_MAP.json",
        BASE_DIR
        / "artifacts"
        / "intel_opposition_detect_intro_evt"
        / "opposition_risk_assessment.json",
    ]

    available = [artifact.name for artifact in required_artifacts if artifact.exists()]
    return len(available) == len(required_artifacts), available


def main():
    """Main orchestration."""
    print("=" * 80)
    print("INTRO_EVT Phase Orchestration")
    print("=" * 80)

    # Check monitoring
    print("\n[1/6] Checking monitoring dashboard...")
    if not check_monitoring():
        print("[WARN] Monitoring dashboard status not found")
        print("  Dashboard should be running before agent spawn")
        print("  Run: python monitoring/dashboard-terminal.py")
        response = input("  Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Orchestration cancelled")
            return
    else:
        print("[OK] Monitoring dashboard status found")

    # Check state
    print("\n[2/6] Verifying legislative state...")
    if not check_state():
        print("[ERR] Current state is not INTRO_EVT")
        print("  Update state file before proceeding")
        return
    print("[OK] State verified: INTRO_EVT")

    log_event("orchestration_started", "INTRO_EVT orchestration started")

    # Spawn intelligence agents
    print("\n[3/6] Spawning intelligence agents...")
    intelligence_agents = [
        "intel_signal_scan_intro_evt.py",
        "intel_stakeholder_map_intro_evt.py",
        "intel_opposition_detect_intro_evt.py",
    ]

    for agent in intelligence_agents:
        if not spawn_agent(agent):
            print(f"[ERR] Failed to spawn {agent}")
            log_event("agent_spawn_failed", f"Failed to spawn {agent}")
        time.sleep(1)  # Brief pause between spawns

    # Wait for intelligence artifacts
    print("\n[4/6] Waiting for intelligence artifacts...")
    max_wait = 30  # seconds
    wait_interval = 2
    waited = 0

    ready = False
    while waited < max_wait:
        ready, available = check_intelligence_artifacts()
        if ready:
            print(f"[OK] All intelligence artifacts available: {', '.join(available)}")
            break
        print(f"  Waiting... ({waited}/{max_wait}s) - Available: {len(available)}/3")
        time.sleep(wait_interval)
        waited += wait_interval

    if not ready:
        print("[WARN] Not all intelligence artifacts available")
        print("  Proceeding anyway - drafting agents may be blocked")

    # Spawn drafting agents
    print("\n[5/6] Spawning drafting agents...")
    drafting_agents = [
        "draft_framing_intro_evt.py",
        "draft_whitepaper_intro_evt.py",
    ]

    for agent in drafting_agents:
        if not spawn_agent(agent):
            print(f"[ERR] Failed to spawn {agent}")
            log_event("agent_spawn_failed", f"Failed to spawn {agent}")
        time.sleep(1)  # Brief pause between spawns

    # Check review queue
    print("\n[6/6] Checking human review queue...")
    review_queue_path = BASE_DIR / "review" / "HR_PRE_queue.json"
    if review_queue_path.exists():
        queue = json.loads(review_queue_path.read_text())
        pending = len(queue.get("pending_reviews", []))
        print(f"[OK] Review queue: {pending} artifact(s) pending HR_PRE approval")
        for review in queue.get("pending_reviews", []):
            print(f"  - {review.get('artifact_type')}: {review.get('artifact_name')}")
    else:
        print("[WARN] No review queue found")

    log_event("orchestration_completed", "INTRO_EVT orchestration completed")

    print("\n" + "=" * 80)
    print("Orchestration Complete")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review artifacts in review/HR_PRE_queue.json")
    print("2. Approve/reject artifacts via HR_PRE gate")
    print("3. After approval, system can advance to COMM_EVT (human authority required)")
    print("\nMonitor agent status:")
    print("  python monitoring/dashboard-terminal.py")


if __name__ == "__main__":
    main()
