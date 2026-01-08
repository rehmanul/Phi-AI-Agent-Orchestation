# Quick Start Guide - Risk Management System

## Prerequisites Check

### Backend
- Python 3.8+
- FastAPI installed (`pip install -r requirements.txt`)

### Frontend
- Node.js 18+
- npm packages installed (`npm install` in frontend directory)
- Recharts library (already in package.json)

---

## Starting the System

### Step 1: Start Backend Server

Open a terminal and run:

```powershell
cd risk-management-system
python -m api.main
```

**Expected Output:**
```
Starting Risk Management System Backend on port 8002
INFO:     Uvicorn running on http://0.0.0.0:8002
```

**Verify:** Open `http://localhost:8002/docs` - Should see Swagger UI

---

### Step 2: Start Frontend Server

Open a **new terminal** and run:

```powershell
cd risk-management-system\frontend
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 16.1.1
  - Local:        http://localhost:3000
```

**Verify:** Open `http://localhost:3000` - Should see dashboard

---

## Testing the Complete Workflow

### 1. Access Dashboard
- Navigate to `http://localhost:3000`
- You should see the Risk Management System dashboard
- Status banner should show "Backend Connected" (green)

### 2. Start New Workflow
- Click "Start New Risk Assessment" or navigate to `/workflow/new`
- Upload a test document (PDF, TXT, or DOCX)
- Click "Upload and Process"

### 3. Navigate Through Phases

**Phase 1: Intake** ✅
- Document uploads and processes
- Assumptions are extracted
- Click "Proceed to Risk Scan" when ready

**Phase 2: Risk Scan** ✅ NEW
- Click "Execute Risk Scan"
- View three columns: Tail Risk, Incentive, Regulatory
- Expand risk cards to see details
- Click "Proceed to Modeling" when complete

**Phase 3: Modeling** ✅ NEW
- Click "Execute Modeling"
- View bounds (Worst/Expected/Best)
- See probability distribution chart
- Review scenario tree and stress tests
- Click "Proceed to Memory" when complete

**Phase 4: Memory** ✅ NEW
- Review historical data
- Check near misses
- View assumption timeline
- Click "Proceed to Ruin Gates" when ready

**Phase 5: Ruin Gates** ✅ NEW (CRITICAL)
- Click "EVALUATE RUIN GATES"
- **Large STOP/PROCEED banner appears**
- Three gate cards show YES/NO results
- If STOP: Review redesign options
- If PROCEED: Click "Continue to Human Review"

**Phase 6: Human Judgment** ✅ NEW
- Fill in reviewer name
- Add review comments
- Select decision: Approve / Request Revisions / Reject
- If rejecting, provide reason
- Click "Approve & Release" or "Reject"

**Phase 7: Execution** ✅ NEW
- View execution timeline
- Monitor status (auto-updates every 5 seconds)
- See model updates
- Review learning outcomes

---

## Verification Checklist

### Backend API
- [ ] Backend starts without errors
- [ ] Swagger UI accessible at `/docs`
- [ ] Health check returns 200 at `/health`
- [ ] All phase endpoints listed in Swagger

### Frontend
- [ ] Frontend starts without errors
- [ ] Dashboard loads
- [ ] Status banner shows backend connection
- [ ] All 7 phases visible in navigation
- [ ] Navigation shows phase status correctly

### Phase Functionality
- [ ] Phase 1: Document upload works
- [ ] Phase 2: Risk scan executes
- [ ] Phase 3: Modeling runs and shows charts
- [ ] Phase 4: Memory data displays
- [ ] Phase 5: Ruin gates evaluate (prominent design)
- [ ] Phase 6: Judgment form validates
- [ ] Phase 7: Execution monitors and updates

### UX Features
- [ ] Loading states appear during operations
- [ ] Error messages show with retry buttons
- [ ] Phase navigation disables locked phases
- [ ] Completed phases show checkmarks
- [ ] Current phase highlighted

---

## Troubleshooting

### Backend Won't Start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8002 is not in use

### Frontend Won't Start
- Check Node version: `node --version` (need 18+)
- Install dependencies: `npm install` in frontend directory
- Check port 3000 is not in use

### API Connection Errors
- Verify backend is running on port 8002
- Check CORS settings in `api/main.py`
- Verify `NEXT_PUBLIC_API_URL` in frontend (defaults to localhost:8002)

### Phase Navigation Issues
- Check workflow state file exists in `data/workflows/`
- Verify workflow_id matches between frontend and backend
- Check browser console for errors

---

## File Locations

### Backend State Files
- Workflow states: `risk-management-system/data/workflows/workflow_*.json`
- Phase results: `risk-management-system/data/processed/{phase_name}/`
- Error logs: `risk-management-system/data/logs/errors/`

### Frontend Build
- Development: `npm run dev` (port 3000)
- Production build: `npm run build` then `npm start`

---

## API Documentation

Full API documentation available at:
- **Swagger UI:** `http://localhost:8002/docs`
- **ReDoc:** `http://localhost:8002/redoc` (if enabled)

---

## Next Steps

1. **Test Complete Workflow**
   - Upload a real document
   - Go through all 7 phases
   - Verify data flows correctly

2. **Review Implementation**
   - Check `IMPLEMENTATION_COMPLETE.md` for details
   - Review code in each phase directory
   - Test error scenarios

3. **Customize as Needed**
   - Adjust styling in Tailwind classes
   - Modify phase layouts
   - Add additional visualizations

---

**System Status:** ✅ Ready for Testing  
**All Phases:** ✅ Implemented  
**Documentation:** ✅ Complete
