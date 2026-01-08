"""
Verification Script - Risk Management System Implementation
Shows progress bars while verifying all components
"""

import sys
import time
from pathlib import Path

def print_progress(step, total, message):
    """Print a progress bar"""
    percent = int((step / total) * 100)
    bar_length = 40
    filled = int(bar_length * step / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    sys.stdout.write(f'\r[{bar}] {percent}% - {message}')
    sys.stdout.flush()
    if step == total:
        print()  # New line when complete

def check_file_exists(filepath, description):
    """Check if a file exists"""
    path = Path(filepath)
    exists = path.exists()
    if exists:
        size = path.stat().st_size
        return True, f"{description}: ✅ ({size} bytes)"
    return False, f"{description}: ❌ NOT FOUND"

def verify_implementation():
    """Verify all implementation components"""
    
    print("\n" + "="*60)
    print("RISK MANAGEMENT SYSTEM - IMPLEMENTATION VERIFICATION")
    print("="*60 + "\n")
    
    total_steps = 25
    step = 0
    
    results = []
    
    # Backend Files
    print("\n📦 BACKEND VERIFICATION")
    print("-" * 60)
    
    step += 1
    print_progress(step, total_steps, "Checking backend files...")
    time.sleep(0.1)
    
    backend_files = [
        ("api/routes/workflow.py", "Workflow routes (enhanced)"),
        ("api/routes/risk_scan.py", "Risk scan routes"),
        ("api/routes/modeling.py", "Modeling routes"),
        ("api/routes/memory.py", "Memory routes"),
        ("api/routes/ruin_gates.py", "Ruin gates routes"),
        ("api/routes/judgment.py", "Judgment routes"),
        ("api/routes/execution.py", "Execution routes"),
        ("agents/orchestrator/workflow_engine.py", "Workflow engine (enhanced)"),
    ]
    
    for filepath, desc in backend_files:
        exists, msg = check_file_exists(filepath, desc)
        results.append((exists, msg))
        step += 1
        print_progress(step, total_steps, f"Checked: {desc}")
        time.sleep(0.05)
    
    # Frontend Phase Pages
    print("\n🎨 FRONTEND VERIFICATION")
    print("-" * 60)
    
    frontend_files = [
        ("frontend/src/app/workflow/[id]/risk_scan/page.tsx", "Phase 2: Risk Scan UI"),
        ("frontend/src/app/workflow/[id]/modeling/page.tsx", "Phase 3: Modeling UI"),
        ("frontend/src/app/workflow/[id]/memory/page.tsx", "Phase 4: Memory UI"),
        ("frontend/src/app/workflow/[id]/ruin_gates/page.tsx", "Phase 5: Ruin Gates UI (CRITICAL)"),
        ("frontend/src/app/workflow/[id]/judgment/page.tsx", "Phase 6: Human Judgment UI"),
        ("frontend/src/app/workflow/[id]/execution/page.tsx", "Phase 7: Execution UI"),
        ("frontend/src/components/PhaseNavigation.tsx", "Phase Navigation (enhanced)"),
        ("frontend/src/components/ErrorBoundary.tsx", "Error Boundary component"),
        ("frontend/src/lib/api.ts", "API Client (all endpoints)"),
    ]
    
    for filepath, desc in frontend_files:
        exists, msg = check_file_exists(filepath, desc)
        results.append((exists, msg))
        step += 1
        print_progress(step, total_steps, f"Checked: {desc}")
        time.sleep(0.05)
    
    # Documentation
    print("\n📚 DOCUMENTATION VERIFICATION")
    print("-" * 60)
    
    docs = [
        ("IMPLEMENTATION_COMPLETE.md", "Implementation summary"),
        ("QUICK_START.md", "Quick start guide"),
        ("README.md", "Main README"),
    ]
    
    for filepath, desc in docs:
        exists, msg = check_file_exists(filepath, desc)
        results.append((exists, msg))
        step += 1
        print_progress(step, total_steps, f"Checked: {desc}")
        time.sleep(0.05)
    
    # Final Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for exists, _ in results if exists)
    total = len(results)
    
    for exists, msg in results:
        print(f"  {msg}")
    
    print("\n" + "-"*60)
    print(f"✅ PASSED: {passed}/{total}")
    print(f"❌ FAILED: {total - passed}/{total}")
    print("-"*60)
    
    if passed == total:
        print("\n🎉 ALL COMPONENTS VERIFIED SUCCESSFULLY!")
        print("\nNext steps:")
        print("  1. Start backend: python -m api.main")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Open browser: http://localhost:3000")
        return 0
    else:
        print(f"\n⚠️  {total - passed} component(s) missing - please check above")
        return 1

if __name__ == "__main__":
    try:
        exit_code = verify_implementation()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during verification: {e}")
        sys.exit(1)
